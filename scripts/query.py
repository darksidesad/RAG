#!/usr/bin/env python3
"""
Script de búsqueda y consulta para RAG.

Busca chunks relevantes en Qdrant y genera respuestas
usando un LLM vía OpenRouter.
"""

import argparse
import os
import sys
from pathlib import Path

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

# ── Configuración ──────────────────────────────────────────────
COLLECTION_NAME = "rag_docs"
EMBEDDING_MODEL = "perplexity/pplx-embed-v1-0.6b"
EMBEDDING_DIMS = 1024
LLM_MODEL = "nex-agi/nex-n2-pro:free"
QDRANT_URL = os.getenv("QDRANT_URL", "https://rag-ejemplo-qdrant.vh9sw0.easypanel.host")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_embedding_client() -> OpenAI:
    """Cliente OpenAI compatible para embeddings via OpenRouter."""
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)


def get_llm_client() -> OpenAI:
    """Cliente OpenAI compatible para LLM via OpenRouter."""
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)


def embed_query(query: str) -> list[float]:
    """Genera embedding para el query."""
    client = get_embedding_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query],
    )
    return response.data[0].embedding


def search_chunks(
    client: QdrantClient,
    query_embedding: list[float],
    empresa: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Busca chunks similares en Qdrant."""
    search_filter = None
    if empresa:
        search_filter = Filter(
            must=[
                FieldCondition(key="empresa", match=MatchValue(value=empresa))
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=search_filter,
        limit=limit,
    )

    chunks = []
    for point in results.points:
        payload = point.payload
        chunks.append({
            "texto": payload.get("texto", ""),
            "empresa": payload.get("empresa", ""),
            "año": payload.get("año", ""),
            "página": payload.get("página", 0),
            "tipo": payload.get("tipo", "texto"),
            "archivo": payload.get("archivo", ""),
            "score": point.score,
        })

    return chunks


def build_context(chunks: list[dict]) -> str:
    """Construye el contexto para el LLM desde los chunks encontrados."""
    if not chunks:
        return "No se encontraron documentos relevantes."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = f"[{chunk['archivo']} - Pág. {chunk['página']}]"
        tipo = f"({chunk['tipo']})"
        score = f"(score: {chunk['score']:.3f})"
        context_parts.append(f"--- Fuente {i} {source} {tipo} {score} ---\n{chunk['texto']}")

    return "\n\n".join(context_parts)


def generate_answer(query: str, context: str) -> str:
    """Genera una respuesta usando el LLM."""
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY no configurada en .env"

    client = get_llm_client()

    system_prompt = """Eres un asistente experto en análisis de documentos empresariales.
Tu tarea es responder preguntas basándote EXCLUSIVAMENTE en el contexto proporcionado.

Reglas:
1. Solo usa la información del contexto proporcionado
2. Si la información no está en el contexto, di "No tengo información suficiente para responder esa pregunta"
3. Cita las fuentes cuando sea posible (archivo y página)
4. Sé preciso y conciso
5. Si hay tablas, interpreta los datos correctamente"""

    user_prompt = f"""Contexto de documentos:
{context}

---
Pregunta: {query}

Responde basándote únicamente en el contexto proporcionado."""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Búsqueda y consulta RAG.")
    parser.add_argument("--query", required=True, help="Pregunta a realizar.")
    parser.add_argument("--empresa", help="Filtrar por empresa (opcional).")
    parser.add_argument("--limit", type=int, default=5, help="Número de resultados (default: 5).")
    parser.add_argument("--no-answer", action="store_true", help="Solo buscar, sin generar respuesta.")
    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY no configurada en .env", file=sys.stderr)
        sys.exit(1)

    print(f"Query: {args.query}")
    if args.empresa:
        print(f"Filtro: empresa={args.empresa}")

    # 1. Generar embedding del query
    print("\n[1/3] Generando embedding del query...")
    query_embedding = embed_query(args.query)

    # 2. Buscar chunks
    print("\n[2/3] Buscando chunks relevantes...")
    qdrant_client = QdrantClient(url=QDRANT_URL, https=True, api_key=QDRANT_API_KEY or None)
    chunks = search_chunks(qdrant_client, query_embedding, args.empresa, args.limit)

    if not chunks:
        print("No se encontraron resultados.")
        sys.exit(0)

    print(f"  → {len(chunks)} resultados encontrados:")

    for i, chunk in enumerate(chunks, 1):
        print(f"\n  [{i}] Score: {chunk['score']:.3f} | {chunk['archivo']} Pág. {chunk['página']}")
        preview = chunk['texto'][:150].replace('\n', ' ')
        print(f"      {preview}...")

    if args.no_answer:
        sys.exit(0)

    # 3. Generar respuesta
    print("\n[3/3] Generando respuesta...")
    context = build_context(chunks)
    answer = generate_answer(args.query, context)

    print("\n" + "=" * 60)
    print("RESPUESTA:")
    print("=" * 60)
    print(answer)
    print("=" * 60)


if __name__ == "__main__":
    main()
