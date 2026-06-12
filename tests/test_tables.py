"""Tests para funciones de tablas."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ingest import table_to_text


class TestTableToText:
    """Tests para table_to_text."""

    def test_empty_table(self):
        assert table_to_text([]) == ""

    def test_single_row_headers_only(self, single_row_table):
        result = table_to_text(single_row_table)
        assert result == "Col1 | Col2 | Col3"

    def test_full_table(self, sample_table):
        result = table_to_text(sample_table)
        lines = result.split("\n")
        assert len(lines) == 4  # header + 3 rows
        assert lines[0] == "Nombre | Edad | Ciudad"
        assert "Ana" in lines[1]
        assert "Madrid" in lines[1]

    def test_table_with_empty_cells(self):
        table = [
            ["A", "B", "C"],
            ["1", "", "3"],
            ["", "5", ""],
        ]
        result = table_to_text(table)
        lines = result.split("\n")
        assert len(lines) == 3
        assert "A | B | C" in lines[0]

    def test_table_with_shorter_rows(self):
        table = [
            ["Col1", "Col2", "Col3"],
            ["Val1", "Val2"],  # Missing third column
        ]
        result = table_to_text(table)
        lines = result.split("\n")
        assert len(lines) == 2
        # Should pad with empty string
        assert "Val1 | Val2 | " in lines[1]

    def test_table_with_longer_rows(self):
        table = [
            ["Col1", "Col2"],
            ["Val1", "Val2", "Extra"],
        ]
        result = table_to_text(table)
        lines = result.split("\n")
        # Should only use first 2 columns
        assert "Val1 | Val2" in lines[1]

    def test_single_column_table(self):
        table = [
            ["Name"],
            ["Alice"],
            ["Bob"],
        ]
        result = table_to_text(table)
        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "Name"

    def test_table_with_special_characters(self):
        table = [
            ["ID", "Description"],
            ["1", "Product | with | pipes"],
        ]
        result = table_to_text(table)
        assert "Product | with | pipes" in result

    def test_preserves_order(self):
        table = [
            ["First", "Second", "Third"],
            ["1", "2", "3"],
            ["4", "5", "6"],
        ]
        result = table_to_text(table)
        lines = result.split("\n")
        assert "First" in lines[0]
        assert "1" in lines[1]
        assert "4" in lines[2]
