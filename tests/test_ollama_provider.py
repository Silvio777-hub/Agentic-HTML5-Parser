"""
tests/test_ollama_provider.py — Tests for OllamaLocalProvider and LLM Provider Factory.

Validates:
- OllamaLocalProvider initialization and configuration
- Graceful connection failure when daemon is offline
- Provider factory get_llm_provider() with various options
- MockLLMProvider deterministic execution
"""

import pytest
from src.llm_provider import (
    OllamaLocalProvider, MockLLMProvider, ClaudeProvider,
    OpenAIProvider, get_llm_provider
)


class TestOllamaAndLLMProviders:
    """Tests for multi-model LLM abstraction layer."""

    def test_ollama_provider_initialization(self):
        provider = OllamaLocalProvider(model_name="llama3.2:latest", host="http://127.0.0.1:11434")
        assert provider.model_name == "llama3.2:latest"
        assert provider.host == "http://127.0.0.1:11434"
        assert provider.timeout == 30.0

    def test_ollama_is_available_graceful_offline(self):
        # Point to a dead/unbound port to test offline detection
        provider = OllamaLocalProvider(host="http://127.0.0.1:59999")
        available = provider.is_available()
        assert available is False

    def test_ollama_list_models_graceful_offline(self):
        provider = OllamaLocalProvider(host="http://127.0.0.1:59999")
        models = provider.list_models()
        assert isinstance(models, list)
        assert len(models) == 0

    def test_ollama_generate_connection_error(self):
        provider = OllamaLocalProvider(host="http://127.0.0.1:59999")
        with pytest.raises(ConnectionError) as exc_info:
            provider.generate("Test prompt")
        assert "Failed to connect to Ollama" in str(exc_info.value)

    def test_mock_llm_provider_generation(self):
        provider = MockLLMProvider(default_response="Generated Code")
        res = provider.generate("Write a parser")
        assert "[mock-model] Generated Code" in res

    def test_get_llm_provider_explicit_mock(self):
        provider = get_llm_provider(provider_type="mock")
        assert isinstance(provider, MockLLMProvider)

    def test_get_llm_provider_explicit_ollama(self):
        provider = get_llm_provider(provider_type="ollama", model_name="mistral:latest")
        assert isinstance(provider, OllamaLocalProvider)
        assert provider.model_name == "mistral:latest"

    def test_get_llm_provider_auto_fallback(self):
        # Without cloud keys and with Ollama offline, should fallback to MockLLMProvider
        provider = get_llm_provider(provider_type="auto")
        assert provider is not None
        assert hasattr(provider, "generate")
