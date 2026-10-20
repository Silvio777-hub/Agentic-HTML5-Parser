"""
src/llm_provider.py — Multi-Model LLM Provider Abstraction.
Enables seamless switching between Claude (Anthropic), OpenAI (GPT-4o),
Ollama (Local Open-Source), and Mock Providers with unified on-disk caching.
"""

import os
import json
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
        res = self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.content[0].text


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
    """Local Open-Source LLM Provider (Llama 3, DeepSeek via Ollama)."""

    def __init__(self, model_name: str = "llama3:latest", host: str = "http://localhost:11434", use_cache: bool = True):
        super().__init__(model_name, use_cache)
        self.host = host

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        import urllib.request
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
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "")


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock Provider for unit testing without API costs."""

    def __init__(self, default_response: str = "Mocked LLM Response"):
        super().__init__("mock-model", use_cache=False)
        self.default_response = default_response

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        return f"[{self.model_name}] {self.default_response}"
