"""Tests para operaciones de Qdrant (con mocks)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ingest import COLLECTION_NAME, EMBEDDING_DIMS, upsert_to_qdrant


class TestUpsertToQdrant:
    """Tests para upsert_to_qdrant con QdrantClient mockeado."""

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_client.get_collections.return_value.collections = []
        self.chunks = [
            {"texto": "chunk 1", "página": 1, "tipo": "texto"},
            {"texto": "chunk 2", "página": 1, "tipo": "tabla"},
        ]
        self.embeddings = [[0.1] * 1536, [0.2] * 1536]

    def test_creates_collection_if_not_exists(self):
        self.mock_client.get_collections.return_value.collections = []

        upsert_to_qdrant(
            self.mock_client,
            self.chunks,
            self.embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        self.mock_client.create_collection.assert_called_once()
        call_kwargs = self.mock_client.create_collection.call_args
        assert call_kwargs.kwargs["collection_name"] == COLLECTION_NAME

    def test_does_not_create_collection_if_exists(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        upsert_to_qdrant(
            self.mock_client,
            self.chunks,
            self.embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        self.mock_client.create_collection.assert_not_called()

    def test_deletes_existing_records(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        upsert_to_qdrant(
            self.mock_client,
            self.chunks,
            self.embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        self.mock_client.delete.assert_called_once()

    def test_upserts_points(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        result = upsert_to_qdrant(
            self.mock_client,
            self.chunks,
            self.embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        self.mock_client.upsert.assert_called_once()
        assert result == 2

    def test_payload_contains_required_fields(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        upsert_to_qdrant(
            self.mock_client,
            self.chunks,
            self.embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        call_args = self.mock_client.upsert.call_args
        points = call_args.kwargs["points"]
        payload = points[0].payload

        assert "texto" in payload
        assert "empresa" in payload
        assert "año" in payload
        assert "página" in payload
        assert "tipo" in payload
        assert "archivo" in payload
        assert "hash" in payload

    def test_payload_values_correct(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        upsert_to_qdrant(
            self.mock_client,
            self.chunks,
            self.embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        call_args = self.mock_client.upsert.call_args
        points = call_args.kwargs["points"]
        payload = points[0].payload

        assert payload["empresa"] == "ACME"
        assert payload["año"] == "2024"
        assert payload["archivo"] == "test.pdf"
        assert payload["hash"] == "abc123"

    def test_returns_correct_count(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        result = upsert_to_qdrant(
            self.mock_client,
            self.chunks,
            self.embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        assert result == len(self.chunks)

    def test_empty_chunks(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        result = upsert_to_qdrant(
            self.mock_client,
            [],
            [],
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        assert result == 0

    def test_batch_upsert_for_large_dataset(self):
        mock_collection = MagicMock()
        mock_collection.name = COLLECTION_NAME
        self.mock_client.get_collections.return_value.collections = [mock_collection]

        # Create 150 chunks to test batching
        chunks = [
            {"texto": f"chunk_{i}", "página": 1, "tipo": "texto"} for i in range(150)
        ]
        embeddings = [[0.1] * 1536 for _ in range(150)]

        result = upsert_to_qdrant(
            self.mock_client,
            chunks,
            embeddings,
            "ACME",
            "2024",
            "abc123",
            "test.pdf",
        )

        # Should be called twice (100 + 50)
        assert self.mock_client.upsert.call_count == 2
        assert result == 150
