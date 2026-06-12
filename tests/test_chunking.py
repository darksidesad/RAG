"""Tests para funciones de chunking."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ingest import _apply_overlap, _split_sentences, chunk_text, count_tokens


class TestCountTokens:
    """Tests para count_tokens."""

    def test_empty_string(self, tokenizer):
        assert count_tokens("", tokenizer) == 0

    def test_single_word(self, tokenizer):
        assert count_tokens("hello", tokenizer) == 1

    def test_sentence(self, tokenizer):
        tokens = count_tokens("Hola, esto es una prueba.", tokenizer)
        assert tokens > 0
        assert tokens < 20

    def test_longer_text(self, tokenizer):
        text = "Esta es una oración de prueba con más palabras para contar tokens."
        tokens = count_tokens(text, tokenizer)
        assert tokens > 5


class TestSplitSentences:
    """Tests para _split_sentences."""

    def test_single_sentence(self):
        result = _split_sentences("Hola mundo.")
        assert result == ["Hola mundo."]

    def test_multiple_sentences(self):
        result = _split_sentences("Primera oración. Segunda oración. Tercera.")
        assert len(result) == 3

    def test_sentence_with_question(self):
        result = _split_sentences("¿Qué pasa? Todo bien.")
        assert len(result) == 2

    def test_empty_string(self):
        result = _split_sentences("")
        assert result == []

    def test_no_period(self):
        result = _split_sentences("Sin punto final")
        assert result == ["Sin punto final"]


class TestChunkText:
    """Tests para chunk_text."""

    def test_empty_text(self, tokenizer):
        result = chunk_text("", 512, 64, tokenizer)
        assert result == []

    def test_whitespace_only(self, tokenizer):
        result = chunk_text("   \n\n   ", 512, 64, tokenizer)
        assert result == []

    def test_short_text_single_chunk(self, tokenizer, short_text):
        result = chunk_text(short_text, 512, 64, tokenizer)
        assert len(result) == 1
        assert result[0] == short_text

    def test_long_text_multiple_chunks(self, tokenizer, long_text):
        result = chunk_text(long_text, 512, 64, tokenizer)
        assert len(result) > 1

    def test_chunks_respect_max_tokens(self, tokenizer, long_text):
        max_tokens = 100
        result = chunk_text(long_text, max_tokens, 10, tokenizer)
        for chunk in result:
            tokens = count_tokens(chunk, tokenizer)
            # Allow some tolerance for paragraph boundaries
            assert tokens <= max_tokens + 50

    def test_overlap_exists(self, tokenizer, long_text):
        max_tokens = 100
        overlap = 20
        result = chunk_text(long_text, max_tokens, overlap, tokenizer)
        if len(result) > 1:
            # Check that some text from end of chunk N appears in chunk N+1
            for i in range(len(result) - 1):
                chunk_end = result[i][-100:]
                # At least some words should appear in next chunk
                words = chunk_end.split()
                if words:
                    assert any(w in result[i + 1] for w in words[-3:])

    def test_paragraphs_not_split_unless_needed(self, tokenizer):
        text = "Párrafo corto.\n\nOtro párrafo corto."
        result = chunk_text(text, 512, 64, tokenizer)
        assert len(result) == 1

    def test_single_chunk(self, tokenizer):
        result = chunk_text("Test.", 512, 64, tokenizer)
        assert len(result) == 1


class TestApplyOverlap:
    """Tests para _apply_overlap."""

    def test_empty_chunk(self, tokenizer):
        result, tokens = _apply_overlap([], 0, 64, tokenizer)
        assert result == []
        assert tokens == 0

    def test_small_overlap(self, tokenizer):
        chunk = ["Primera oración.", "Segunda oración.", "Tercera oración."]
        total_tokens = sum(count_tokens(s, tokenizer) for s in chunk)
        result, tokens = _apply_overlap(chunk, total_tokens, 10, tokenizer)
        assert len(result) <= len(chunk)
        assert tokens <= 10 + 5  # Small tolerance

    def test_large_overlap_keeps_all(self, tokenizer):
        chunk = ["Short."]
        result, tokens = _apply_overlap(chunk, 1, 1000, tokenizer)
        assert result == ["Short."]
