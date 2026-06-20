import os
import pytest
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction, OpenAIEmbeddingFunction
from src.core.rag.retriever import get_embedding_function, GeminiEmbeddingFunction

def test_get_embedding_function_local(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "local")
    fn = get_embedding_function()
    assert isinstance(fn, SentenceTransformerEmbeddingFunction)


def test_get_embedding_function_openai_missing_key(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc:
        get_embedding_function()
    assert "OPENAI_API_KEY is required" in str(exc.value)


def test_get_embedding_function_openai_with_key(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    fn = get_embedding_function()
    assert isinstance(fn, OpenAIEmbeddingFunction)


def test_get_embedding_function_gemini_missing_key(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc:
        get_embedding_function()
    assert "GEMINI_API_KEY or GOOGLE_API_KEY is required" in str(exc.value)


def test_get_embedding_function_gemini_with_key(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    fn = get_embedding_function()
    assert isinstance(fn, GeminiEmbeddingFunction)
    assert fn.api_key == "test-gemini-key"
