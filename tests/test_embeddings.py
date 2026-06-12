"""Tests para generación de embeddings (con mocks)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ingest import generate_embeddings


class TestGenerateEmbeddings:
    """Tests para generate_embeddings con OpenAI mockeado."""

    @patch("ingest.OpenAI")
    def test_single_text(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        result = generate_embeddings(["hello"])

        assert len(result) == 1
        assert len(result[0]) == 1536

    @patch("ingest.OpenAI")
    def test_multiple_texts(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
            MagicMock(embedding=[0.3] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response

        result = generate_embeddings(["text1", "text2", "text3"])

        assert len(result) == 3

    @patch("ingest.OpenAI")
    def test_uses_correct_model(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        generate_embeddings(["test"])

        mock_client.embeddings.create.assert_called_once()
        call_kwargs = mock_client.embeddings.create.call_args
        assert call_kwargs.kwargs["model"] == "text-embedding-3-small"

    @patch("ingest.OpenAI")
    def test_uses_correct_dimensions(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        generate_embeddings(["test"])

        call_kwargs = mock_client.embeddings.create.call_args
        assert call_kwargs.kwargs["dimensions"] == 1536

    @patch("ingest.OpenAI")
    def test_batch_size_limit(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Create 250 texts to test batching
        texts = [f"text_{i}" for i in range(250)]

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536) for _ in range(200)]
        mock_client.embeddings.create.return_value = mock_response

        result = generate_embeddings(texts)

        # Should be called twice (200 + 50)
        assert mock_client.embeddings.create.call_count == 2

    @patch("ingest.OpenAI")
    def test_empty_list(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        result = generate_embeddings([])

        assert result == []
        mock_client.embeddings.create.assert_not_called()
