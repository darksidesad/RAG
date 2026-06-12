"""Tests para file_hash."""

import hashlib
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ingest import file_hash


class TestFileHash:
    """Tests para file_hash."""

    def test_hash_consistent(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("contenido de prueba")

        hash1 = file_hash(str(test_file))
        hash2 = file_hash(str(test_file))

        assert hash1 == hash2

    def test_hash_different_for_different_files(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("contenido uno")
        file2.write_text("contenido dos")

        hash1 = file_hash(str(file1))
        hash2 = file_hash(str(file2))

        assert hash1 != hash2

    def test_hash_is_sha256(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = file_hash(str(test_file))

        # SHA-256 hex digest is 64 characters
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_matches_manual_calculation(self, tmp_path):
        test_file = tmp_path / "test.txt"
        content = b"test content"
        test_file.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()
        result = file_hash(str(test_file))

        assert result == expected

    def test_hash_empty_file(self, tmp_path):
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        result = file_hash(str(test_file))

        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_hash_binary_file(self, tmp_path):
        test_file = tmp_path / "binary.bin"
        test_file.write_bytes(bytes(range(256)))

        result = file_hash(str(test_file))

        assert len(result) == 64
