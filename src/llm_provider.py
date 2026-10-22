"""
src/llm_provider.py — Multi-Model LLM Provider Abstraction.
Enables seamless switching between Claude (Anthropic), OpenAI (GPT-4o),
Ollama (Local Open-Source), and Mock Providers with unified on-disk caching.
"""

import os
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

try:
    from src.cache import ResponseCache
    _GLOBAL_CACHE = ResponseCache()
except Exception:
    _GLOBAL_CACHE = None


class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""

    def __init__(self, model_name: str, use_cache: bool = True):
        self.model_name = model_name
        self.use_cache = use_cache

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate response from LLM."""
        pass

    def call(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Call LLM with transparent disk caching."""
        provider_name = self.__class__.__name__
        cache_key = f"{self.model_name}::{system_prompt or ''}::{prompt}"

        if self.use_cache and _GLOBAL_CACHE:
            cached = _GLOBAL_CACHE.get(provider_name, cache_key)
            if cached is not None:
                return cached

        response = self.generate(prompt, system_prompt=system_prompt, temperature=temperature)

        if self.use_cache and _GLOBAL_CACHE:
            _GLOBAL_CACHE.set(provider_name, cache_key, response)

        return response


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude LLM Provider."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None, use_cache: bool = True):
        super().__init__(model_name, use_cache)
        from anthropic import Anthropic
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        if not self.client:
            raise ValueError("Anthropic API key is required for ClaudeProvider.")
        try:
            res = self.client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.content[0].text
        except Exception as e:
            print(f"[ClaudeProvider] API call failed ({e}), falling back to deterministic mock.")
            return MockLLMProvider().generate(prompt, system_prompt, temperature)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4o LLM Provider."""

    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, use_cache: bool = True):
        super().__init__(model_name, use_cache)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            res = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
            return res.choices[0].message.content
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")


class OllamaLocalProvider(BaseLLMProvider):
    """
    Local Open-Source LLM Provider (Llama 3, DeepSeek, Mistral via Ollama).
    Enables 100% offline, zero-cost neural agent execution without cloud API keys.
    """

    def __init__(
        self,
        model_name: str = "llama3.2:latest",
        host: Optional[str] = None,
        timeout: float = 30.0,
        use_cache: bool = True
    ):
        super().__init__(model_name, use_cache)
        self.host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", headers={"User-Agent": "Agentic-HTML5-Parser"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """List locally pulled models in Ollama."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", headers={"User-Agent": "Agentic-HTML5-Parser"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [m.get("name") for m in data.get("models", [])]
        except Exception:
            return []

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Call Ollama /api/generate endpoint."""
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Failed to connect to Ollama at {self.host} ({e}). "
                "Ensure Ollama is running locally: 'ollama serve'."
            ) from e


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock Provider for unit testing and offline fallbacks without API costs."""

    def __init__(self, default_response: str = "Mocked LLM Response"):
        super().__init__("mock-model", use_cache=False)
        self.default_response = default_response

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        return f"[{self.model_name}] {self.default_response}"


def get_llm_provider(
    provider_type: Optional[str] = None,
    model_name: Optional[str] = None,
    use_cache: bool = True,
    **kwargs
) -> BaseLLMProvider:
    """
    Factory function to instantiate the best available LLM provider.
    
    Args:
        provider_type: 'claude', 'openai', 'ollama', 'mock', or 'auto' (default)
        model_name: Optional override for model identifier
        use_cache: Whether to use disk response caching
        **kwargs: Provider-specific arguments (api_key, host, etc.)
    """
    p_type = (provider_type or os.getenv("LLM_PROVIDER", "auto")).lower()

    if p_type == "claude":
        return ClaudeProvider(model_name=model_name or "claude-3-5-sonnet-20241022", use_cache=use_cache, **kwargs)
    elif p_type == "openai":
        return OpenAIProvider(model_name=model_name or "gpt-4o", use_cache=use_cache, **kwargs)
    elif p_type == "ollama":
        return OllamaLocalProvider(model_name=model_name or "llama3.2:latest", use_cache=use_cache, **kwargs)
    elif p_type == "mock":
        return MockLLMProvider(**kwargs)

    # Automatic provider selection based on environment and local availability
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        return ClaudeProvider(model_name=model_name or "claude-3-5-sonnet-20241022", use_cache=use_cache, **kwargs)
    elif os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY").startswith("sk-"):
        return OpenAIProvider(model_name=model_name or "gpt-4o", use_cache=use_cache, **kwargs)

    # Check if local Ollama daemon is active
    ollama = OllamaLocalProvider(model_name=model_name or "llama3.2:latest", use_cache=use_cache, **kwargs)
    if ollama.is_available():
        return ollama

    # Fallback to deterministic mock provider
    return MockLLMProvider(**kwargs)
