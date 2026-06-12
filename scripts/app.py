#!/usr/bin/env python3
"""
Interfaz web moderna para el sistema RAG.
Streamlit app para ingestión y búsqueda de documentos.
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).parent.parent / ".env")

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from ingest import (
    build_chunks,
    extract_pdf_content,
    generate_embeddings,
    upsert_to_qdrant,
    file_hash,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
LLM_MODEL = "nex-agi/nex-n2-pro:free"

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="mi-rag | Document Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
    }
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    .stMetric {
        background: linear-gradient(135deg, #1e1e3f 0%, #2a2a5a 100%);
        border: 1px solid #3a3a6a;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .stMetric label {
        color: #8888cc !important;
        font-size: 0.9rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 2rem !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
    }
    .stTextInput > div > div > input {
        background: #1e1e3f;
        border: 1px solid #3a3a6a;
        border-radius: 8px;
        color: white;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    .stSelectbox > div > div {
        background: #1e1e3f;
        border: 1px solid #3a3a6a;
        border-radius: 8px;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .stMarkdown {
        color: #cccccc;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a 0%, #151530 100%);
        border-right: 1px solid #2a2a5a;
    }
    .uploadedFile {
        background: #1e1e3f;
        border: 1px solid #3a3a6a;
        border-radius: 8px;
    }
    .stAlert {
        background: #1e1e3f;
        border-radius: 8px;
    }
    .search-result {
        background: linear-gradient(135deg, #1e1e3f 0%, #252550 100%);
        border: 1px solid #3a3a6a;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .search-result:hover {
        border-color: #00d4ff;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
    }
    .score-badge {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .tipo-texto {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
    }
    .tipo-tabla {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
    }
    .answer-box {
        background: linear-gradient(135deg, #1e3a2f 0%, #1a4a3a 100%);
        border: 1px solid #2a6a4a;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ─────────────────────────────────────────
def get_qdrant_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL", "https://rag-ejemplo-qdrant.vh9sw0.easypanel.host")
    return QdrantClient(url=url, https=True, api_key=QDRANT_API_KEY or None)


def get_collection_stats(client: QdrantClient) -> dict:
    try:
        collections = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            return {"total_points": 0, "empresas": [], "exists": False}

        info = client.get_collection(COLLECTION_NAME)
        return {
            "total_points": info.points_count or 0,
            "exists": True,
        }
    except Exception:
        return {"total_points": 0, "empresas": [], "exists": False}


def get_empresas(client: QdrantClient) -> list[str]:
    try:
        if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
            return []
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=[0.0] * EMBEDDING_DIMS,
            limit=1000,
        )
        empresas = set()
        for point in results.points:
            if point.payload and "empresa" in point.payload:
                empresas.add(point.payload["empresa"])
        return sorted(list(empresas))
    except Exception:
        return []


def embed_query(query: str) -> list[float]:
    """Genera embedding para el query vía OpenRouter."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY no configurada")
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    return response.data[0].embedding


def generate_answer(query: str, context: str) -> str:
    """Genera respuesta con LLM vía OpenRouter."""
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY no configurada"

    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

    system_prompt = """Eres un asistente experto en análisis de documentos empresariales.
Responde basándote EXCLUSIVAMENTE en el contexto proporcionado.
Si no hay suficiente información, di "No tengo información suficiente".
Cita fuentes cuando sea posible."""

    user_prompt = f"""Contexto:
{context}

---
Pregunta: {query}

Respuesta:"""

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


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## mi-rag")
    st.markdown("Document Intelligence Platform")

    st.divider()

    page = st.radio(
        "Navegación",
        ["Home", "Ingesta", "Chat RAG", "Colecciones"],
        label_visibility="collapsed",
    )

    st.divider()

    # Connection status
    client = get_qdrant_client()
    stats = get_collection_stats(client)

    if stats["exists"]:
        st.success("Qdrant conectado")
        st.metric("Documentos", stats["total_points"])
    else:
        st.warning("Sin conexión")

    st.divider()

    # API Status
    if OPENROUTER_API_KEY:
        st.success("OpenRouter API")
    else:
        st.error("Sin OPENROUTER_API_KEY")


# ── Pages ────────────────────────────────────────────────────
if page == "Home":
    st.markdown("# Document Intelligence Platform")
    st.markdown("Plataforma RAG para ingestión y búsqueda semántica de documentos.")

    st.divider()

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Documentos", stats["total_points"])

    with col2:
        empresas = get_empresas(client)
        st.metric("Empresas", len(empresas))

    with col3:
        st.metric("Colección", "rag_docs" if stats["exists"] else "—")

    with col4:
        st.metric("Estado", "Activo" if stats["exists"] else "Inactivo")

    st.divider()

    # Model info
    st.markdown("### Modelos en Uso")
    mcol1, mcol2 = st.columns(2)

    with mcol1:
        st.info(f"**Embeddings:** {EMBEDDING_MODEL}")

    with mcol2:
        st.info(f"**LLM:** {LLM_MODEL}")

    st.divider()

    # Recent activity
    st.markdown("### Actividad Reciente")
    if stats["exists"] and stats["total_points"] > 0:
        st.info(f"Base de datos activa con {stats['total_points']} documentos indexados.")
    else:
        st.info("No hay documentos indexados aún. Sube tu primer documento para comenzar.")


elif page == "Ingesta":
    st.markdown("# Ingesta de Documentos")
    st.markdown("Sube un PDF para extraer, chunking y almacenar en la base de datos.")

    st.divider()

    with st.form("ingest_form"):
        col1, col2 = st.columns(2)

        with col1:
            pdf_file = st.file_uploader(
                "Documento PDF",
                type=["pdf"],
                help="Arrastra o selecciona un archivo PDF"
            )

        with col2:
            empresa = st.text_input(
                "Empresa",
                placeholder="Ej: ACME Corp",
                help="Nombre de la empresa dueña del documento"
            )
            año = st.text_input(
                "Año",
                placeholder="Ej: 2024",
                help="Año del documento"
            )

        submitted = st.form_submit_button("Procesar Documento", use_container_width=True)

    if submitted:
        if not pdf_file:
            st.error("Por favor selecciona un archivo PDF.")
        elif not empresa:
            st.error("Por favor ingresa el nombre de la empresa.")
        elif not año:
            st.error("Por favor ingresa el año.")
        elif not OPENROUTER_API_KEY:
            st.error("OPENROUTER_API_KEY no configurada en .env")
        else:
            with st.spinner("Procesando documento..."):
                # Save uploaded file
                temp_path = Path(f"/tmp/{pdf_file.name}")
                temp_path.write_bytes(pdf_file.read())

                try:
                    # 1. Extract
                    st.markdown("**1/4** Extrayendo contenido...")
                    pdf_content = extract_pdf_content(str(temp_path))
                    st.success(f"Extraído: {len(pdf_content)} páginas")

                    # 2. Chunk
                    st.markdown("**2/4** Generando chunks...")
                    chunks = build_chunks(pdf_content)
                    text_count = sum(1 for c in chunks if c["tipo"] == "texto")
                    table_count = sum(1 for c in chunks if c["tipo"] == "tabla")
                    st.success(f"Generados: {len(chunks)} chunks ({text_count} texto, {table_count} tablas)")

                    # 3. Embeddings
                    st.markdown("**3/4** Generando embeddings...")
                    texts = [c["texto"] for c in chunks]
                    embeddings = generate_embeddings(texts)
                    st.success(f"Embeddings: {len(embeddings)} generados")

                    # 4. Store
                    st.markdown("**4/4** Almacenando en Qdrant...")
                    f_hash = file_hash(str(temp_path))
                    count = upsert_to_qdrant(
                        client, chunks, embeddings, empresa, año, f_hash, pdf_file.name
                    )
                    st.success(f"Almacenados: {count} chunks")

                    st.divider()
                    st.success("Documento procesado exitosamente!")

                    # Show summary
                    st.markdown("### Resumen")
                    st.json({
                        "archivo": pdf_file.name,
                        "empresa": empresa,
                        "año": año,
                        "paginas": len(pdf_content),
                        "chunks": len(chunks),
                        "texto": text_count,
                        "tablas": table_count,
                    })

                except Exception as e:
                    st.error(f"Error procesando: {e}")
                finally:
                    temp_path.unlink(missing_ok=True)


elif page == "Chat RAG":
    st.markdown("# Chat con tus Documentos")
    st.markdown("Haz preguntas y recibe respuestas basadas en tus documentos.")

    st.divider()

    # Chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Escribe tu pregunta..."):
        if not OPENROUTER_API_KEY:
            st.error("OPENROUTER_API_KEY no configurada en .env")
        else:
            # Show user message
            st.chat_message("user").write(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.spinner("Buscando y generando respuesta..."):
                try:
                    # 1. Embed query
                    query_embedding = embed_query(prompt)

                    # 2. Search
                    results = client.query_points(
                        collection_name=COLLECTION_NAME,
                        query=query_embedding,
                        limit=5,
                    )

                    # 3. Build context
                    context_parts = []
                    sources = []
                    for point in results.points:
                        p = point.payload
                        context_parts.append(
                            f"[{p.get('archivo', '')} Pág.{p.get('página', '')}] {p.get('texto', '')}"
                        )
                        sources.append(f"{p.get('archivo', '')} Pág.{p.get('página', '')}")

                    context = "\n\n".join(context_parts) if context_parts else "No hay documentos."

                    # 4. Generate answer
                    answer = generate_answer(prompt, context)

                    # Show answer
                    st.chat_message("assistant").write(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

                    # Show sources
                    if sources:
                        with st.expander("Fuentes consultadas"):
                            for s in set(sources):
                                st.markdown(f"  {s}")

                except Exception as e:
                    st.error(f"Error: {e}")


elif page == "Colecciones":
    st.markdown("# Gestión de Colecciones")
    st.markdown("Administra la base de datos vectorial.")

    st.divider()

    if not stats["exists"]:
        st.warning("La colección 'rag_docs' no existe aún. Se creará automáticamente al ingerir el primer documento.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Estadísticas")
            st.metric("Total de Puntos", stats["total_points"])

        with col2:
            st.markdown("### Empresas")
            empresas_list = get_empresas(client)
            if empresas_list:
                for emp in empresas_list:
                    st.markdown(f"  {emp}")
            else:
                st.info("Sin empresas registradas.")

        st.divider()

        # Danger zone
        st.markdown("### Zona de Peligro")
        with st.expander("Eliminar colección"):
            st.warning("Esta acción eliminará todos los documentos de la colección.")
            if st.button("Eliminar rag_docs", type="primary"):
                try:
                    client.delete_collection(COLLECTION_NAME)
                    st.success("Colección eliminada.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
