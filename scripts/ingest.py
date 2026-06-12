#!/usr/bin/env python3
"""
Script de ingestión de PDFs para RAG.

Extrae texto y tablas de un PDF, genera embeddings con OpenRouter
y los almacena en Qdrant con metadata (empresa, año, página, tipo).
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

import pdfplumber
import tiktoken
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

# ── Configuración ──────────────────────────────────────────────
COLLECTION_NAME = "rag_docs"
EMBEDDING_MODEL = "perplexity/pplx-embed-v1-0.6b"
EMBEDDING_DIMS = 1024
CHUNK_TOKENS = 512
CHUNK_OVERLAP = 64
QDRANT_URL = os.getenv("QDRANT_URL", "https://rag-ejemplo-qdrant.vh9sw0.easypanel.host")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_tokenizer() -> tiktoken.Encoding:
    """Retorna el tokenizer para contar tokens."""
    return tiktoken.encoding_for_model("gpt-4o")


def count_tokens(text: str, enc: tiktoken.Encoding) -> int:
    """Cuenta tokens en un texto."""
    return len(enc.encode(text))


def chunk_text(
    text: str, max_tokens: int, overlap: int, enc: tiktoken.Encoding
) -> list[str]:
    """
    Divide texto en chunks de max_tokens con overlap.
    Respeta párrafos cuando es posible.
    """
    if not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = count_tokens(para, enc)

        # Si un párrafo solo ya supera el límite, dividir por oraciones
        if para_tokens > max_tokens:
            sentences = _split_sentences(para)
            for sent in sentences:
                sent_tokens = count_tokens(sent, enc)
                if current_tokens + sent_tokens > max_tokens and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    # Overlap: conservar las últimas oraciones que quepan
                    current_chunk, current_tokens = _apply_overlap(
                        current_chunk, current_tokens, overlap, enc
                    )
                current_chunk.append(sent)
                current_tokens += sent_tokens
            continue

        if current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk, current_tokens = _apply_overlap(
                current_chunk, current_tokens, overlap, enc
            )

        current_chunk.append(para)
        current_tokens += para_tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Divide texto en oraciones de forma simple."""
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in sentences if s.strip()]


def _apply_overlap(
    current_chunk: list[str], current_tokens: int, overlap: int, enc: tiktoken.Encoding
) -> tuple[list[str], int]:
    """Mantiene las últimas oraciones del chunk actual como overlap."""
    overlap_chunk: list[str] = []
    overlap_tokens = 0

    for sent in reversed(current_chunk):
        sent_tokens = count_tokens(sent, enc)
        if overlap_tokens + sent_tokens > overlap:
            break
        overlap_chunk.insert(0, sent)
        overlap_tokens += sent_tokens

    return overlap_chunk, overlap_tokens


def extract_pdf_content(pdf_path: str) -> list[dict]:
    """
    Extrae texto y tablas de cada página del PDF.

    Retorna lista de dicts con:
      - page_num: número de página (1-indexed)
      - text: texto extraído
      - tables: lista de tablas (cada tabla es lista de filas)
    """
    content = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text() or ""
            page_tables = page.extract_tables() or []

            # Limpiar tablas: quitar filas vacías y normalizar
            clean_tables = []
            for table in page_tables:
                cleaned = [
                    [cell.strip() if cell else "" for cell in row]
                    for row in table
                    if any(cell and cell.strip() for cell in row)
                ]
                if cleaned:
                    clean_tables.append(cleaned)

            content.append(
                {
                    "page_num": i,
                    "text": page_text.strip(),
                    "tables": clean_tables,
                }
            )
    return content


def table_to_text(table: list[list[str]]) -> str:
    """Convierte una tabla estructurada a texto legible."""
    if not table:
        return ""
    headers = table[0]
    rows = table[1:] if len(table) > 1 else []
    lines = [" | ".join(headers)]
    for row in rows:
        # Pad shorter rows
        padded = row + [""] * (len(headers) - len(row))
        lines.append(" | ".join(padded[: len(headers)]))
    return "\n".join(lines)


def build_chunks(pdf_content: list[dict]) -> list[dict]:
    """
    Construye chunks del contenido del PDF.
    - Texto: chunking con overlap
    - Tablas: chunk completo sin dividir
    """
    enc = get_tokenizer()
    all_chunks = []

    for page in pdf_content:
        page_num = page["page_num"]

        # Chunks de texto
        if page["text"]:
            text_chunks = chunk_text(page["text"], CHUNK_TOKENS, CHUNK_OVERLAP, enc)
            for chunk_text_val in text_chunks:
                all_chunks.append(
                    {
                        "texto": chunk_text_val,
                        "página": page_num,
                        "tipo": "texto",
                    }
                )

        # Tablas como chunks completos
        for table in page["tables"]:
            table_text = table_to_text(table)
            if table_text.strip():
                all_chunks.append(
                    {
                        "texto": table_text,
                        "página": page_num,
                        "tipo": "tabla",
                    }
                )

    return all_chunks


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Genera embeddings usando OpenRouter (perplexity/pplx-embed-v1-0.6b)."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY no configurada en .env")

    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )

    all_embeddings = []
    batch_size = 20  # OpenRouter tiene límites más bajos

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def file_hash(pdf_path: str) -> str:
    """Calcula hash SHA-256 del archivo PDF."""
    sha256 = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def upsert_to_qdrant(
    client: QdrantClient,
    chunks: list[dict],
    embeddings: list[list[float]],
    empresa: str,
    año: str,
    pdf_hash: str,
    pdf_name: str,
) -> int:
    """
    Inserta chunks en Qdrant. Si ya existen registros del mismo archivo,
    los elimina primero (sobrescribe).

    Retorna cantidad de puntos insertados.
    """
    # Verificar/crear colección
    try:
        collections = [c.name for c in client.get_collections().collections]
    except Exception as e:
        print(f"Error conectando a Qdrant: {e}", file=sys.stderr)
        raise
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMS,
                distance=Distance.COSINE,
            ),
        )

    # Eliminar registros existentes del mismo archivo
    existing_filter = Filter(
        must=[
            FieldCondition(key="empresa", match=MatchValue(value=empresa)),
            FieldCondition(key="archivo", match=MatchValue(value=pdf_name)),
        ]
    )
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=existing_filter,
        )
    except Exception:
        pass  # Colección nueva o sin puntos, continuar

    # Preparar puntos
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = abs(hash(f"{pdf_hash}_{i}")) % (2**63)
        payload = {
            "texto": chunk["texto"],
            "empresa": empresa,
            "año": str(año),
            "página": chunk["página"],
            "tipo": chunk["tipo"],
            "archivo": pdf_name,
            "hash": pdf_hash,
        }
        points.append(PointStruct(id=point_id, vector=embedding, payload=payload))

    # Upsert en lotes
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)

    return len(points)


def main():
    parser = argparse.ArgumentParser(description="Ingesta de PDFs para RAG con Qdrant.")
    parser.add_argument("--pdf", required=True, help="Ruta al archivo PDF a procesar.")
    parser.add_argument(
        "--empresa", required=True, help="Nombre de la empresa dueña del documento."
    )
    parser.add_argument("--año", required=True, help="Año del documento.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: archivo no encontrado: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if not pdf_path.suffix.lower() == ".pdf":
        print(f"Error: el archivo no es un PDF: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Procesando: {pdf_path.name}")
    print(f"Empresa:    {args.empresa}")
    print(f"Año:        {args.año}")

    # 1. Extraer contenido del PDF
    print("\n[1/4] Extrayendo texto y tablas del PDF...")
    pdf_content = extract_pdf_content(str(pdf_path))
    total_pages = len(pdf_content)
    print(f"  → {total_pages} páginas procesadas")

    # 2. Construir chunks
    print("\n[2/4] Generando chunks...")
    chunks = build_chunks(pdf_content)
    text_chunks = sum(1 for c in chunks if c["tipo"] == "texto")
    table_chunks = sum(1 for c in chunks if c["tipo"] == "tabla")
    print(
        f"  → {len(chunks)} chunks totales ({text_chunks} texto, {table_chunks} tablas)"
    )

    if not chunks:
        print("Advertencia: no se extrajo contenido del PDF.", file=sys.stderr)
        sys.exit(0)

    # 3. Generar embeddings
    print("\n[3/4] Generando embeddings (OpenRouter)...")
    texts = [c["texto"] for c in chunks]
    embeddings = generate_embeddings(texts)
    print(f"  → {len(embeddings)} embeddings generados")

    # 4. Almacenar en Qdrant
    print("\n[4/4] Almacenando en Qdrant...")
    client = QdrantClient(url=QDRANT_URL, https=True, api_key=QDRANT_API_KEY or None)
    f_hash = file_hash(str(pdf_path))
    count = upsert_to_qdrant(
        client, chunks, embeddings, args.empresa, args.año, f_hash, pdf_path.name
    )
    print(f"  → {count} chunks insertados en colección '{COLLECTION_NAME}'")

    print("\n✓ Ingestión completada exitosamente.")


if __name__ == "__main__":
    main()
