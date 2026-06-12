"""Shared fixtures for tests."""

import pytest
import tiktoken


@pytest.fixture
def tokenizer() -> tiktoken.Encoding:
    """Retorna el tokenizer para tests."""
    return tiktoken.encoding_for_model("gpt-4o")


@pytest.fixture
def short_text() -> str:
    """Texto corto para tests de chunking."""
    return (
        "Este es un párrafo de prueba. Tiene varias oraciones.\n\n"
        "Este es otro párrafo. También tiene oraciones de prueba."
    )


@pytest.fixture
def long_text() -> str:
    """Texto largo que excede 512 tokens para forzar múltiples chunks."""
    paragraphs = []
    for i in range(50):
        paragraphs.append(
            f"Este es el párrafo número {i} del texto de prueba. "
            f"Contiene información relevante para validar el chunking. "
            f"Cada párrafo tiene varias oraciones para completar tokens."
        )
    return "\n\n".join(paragraphs)


@pytest.fixture
def sample_table() -> list[list[str]]:
    """Tabla de ejemplo para tests."""
    return [
        ["Nombre", "Edad", "Ciudad"],
        ["Ana", "25", "Madrid"],
        ["Bob", "30", "Barcelona"],
        ["Carlos", "35", "Valencia"],
    ]


@pytest.fixture
def empty_table() -> list[list[str]]:
    """Tabla vacía."""
    return []


@pytest.fixture
def single_row_table() -> list[list[str]]:
    """Tabla con solo headers."""
    return [["Col1", "Col2", "Col3"]]


@pytest.fixture
def sample_pdf_content() -> list[dict]:
    """Contenido de PDF de ejemplo para tests."""
    return [
        {
            "page_num": 1,
            "text": "Primer página con algo de texto.",
            "tables": [],
        },
        {
            "page_num": 2,
            "text": "Segunda página con más contenido.",
            "tables": [
                [["A", "B"], ["1", "2"]],
            ],
        },
    ]
