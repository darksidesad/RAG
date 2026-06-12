"""Tests para extracción de PDF (con mocks)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ingest import build_chunks, extract_pdf_content


class TestExtractPdfContent:
    """Tests para extract_pdf_content con pdfplumber mockeado."""

    @patch("ingest.pdfplumber.open")
    def test_single_page_no_tables(self, mock_open):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto de prueba."
        mock_page.extract_tables.return_value = []

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf

        result = extract_pdf_content("test.pdf")

        assert len(result) == 1
        assert result[0]["page_num"] == 1
        assert result[0]["text"] == "Texto de prueba."
        assert result[0]["tables"] == []

    @patch("ingest.pdfplumber.open")
    def test_multiple_pages(self, mock_open):
        pages = []
        for i in range(3):
            page = MagicMock()
            page.extract_text.return_value = f"Página {i + 1}"
            page.extract_tables.return_value = []
            pages.append(page)

        mock_pdf = MagicMock()
        mock_pdf.pages = pages
        mock_open.return_value.__enter__.return_value = mock_pdf

        result = extract_pdf_content("test.pdf")

        assert len(result) == 3
        for i in range(3):
            assert result[i]["page_num"] == i + 1
            assert result[i]["text"] == f"Página {i + 1}"

    @patch("ingest.pdfplumber.open")
    def test_page_with_tables(self, mock_open):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto con tabla."
        mock_page.extract_tables.return_value = [
            [["H1", "H2"], ["A", "B"]],
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf

        result = extract_pdf_content("test.pdf")

        assert len(result) == 1
        assert len(result[0]["tables"]) == 1
        assert result[0]["tables"][0] == [["H1", "H2"], ["A", "B"]]

    @patch("ingest.pdfplumber.open")
    def test_empty_page(self, mock_open):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        mock_page.extract_tables.return_value = None

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf

        result = extract_pdf_content("test.pdf")

        assert len(result) == 1
        assert result[0]["text"] == ""
        assert result[0]["tables"] == []

    @patch("ingest.pdfplumber.open")
    def test_table_with_empty_rows(self, mock_open):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_page.extract_tables.return_value = [
            [["H1", "H2"], [], ["A", "B"], [None, None]],
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf

        result = extract_pdf_content("test.pdf")

        # Empty rows should be filtered out
        assert len(result[0]["tables"]) == 1
        assert result[0]["tables"][0] == [["H1", "H2"], ["A", "B"]]


class TestBuildChunks:
    """Tests para build_chunks."""

    def test_empty_content(self):
        result = build_chunks([])
        assert result == []

    def test_text_only(self, sample_pdf_content):
        # Remove tables from sample
        for page in sample_pdf_content:
            page["tables"] = []

        result = build_chunks(sample_pdf_content)

        assert len(result) > 0
        for chunk in result:
            assert chunk["tipo"] == "texto"

    def test_tables_only(self):
        content = [
            {
                "page_num": 1,
                "text": "",
                "tables": [[["A", "B"], ["1", "2"]]],
            }
        ]
        result = build_chunks(content)

        assert len(result) == 1
        assert result[0]["tipo"] == "tabla"
        assert "A" in result[0]["texto"]

    def test_mixed_content(self, sample_pdf_content):
        result = build_chunks(sample_pdf_content)

        text_chunks = [c for c in result if c["tipo"] == "texto"]
        table_chunks = [c for c in result if c["tipo"] == "tabla"]

        assert len(text_chunks) > 0
        assert len(table_chunks) > 0

    def test_page_number_preserved(self, sample_pdf_content):
        result = build_chunks(sample_pdf_content)

        pages = {c["página"] for c in result}
        assert 1 in pages
        assert 2 in pages

    def test_tables_not_split(self):
        # Create a large table that would exceed chunk size if split
        large_table = [["Col" + str(i) for i in range(20)]]
        for row_num in range(50):
            large_table.append([f"R{row_num}C{i}" for i in range(20)])

        content = [
            {
                "page_num": 1,
                "text": "",
                "tables": [large_table],
            }
        ]
        result = build_chunks(content)

        # Table should be a single chunk
        table_chunks = [c for c in result if c["tipo"] == "tabla"]
        assert len(table_chunks) == 1
