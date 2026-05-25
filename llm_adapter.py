"""
llm_adapter.py

Provides a small pluggable adapter that either calls a real LLM provider
when API keys are present (adapter point) or falls back to a deterministic
stub for offline testing.

Usage:
    from llm_adapter import LLMAdapter
    adapter = LLMAdapter()
    response = adapter.generate("Summarize: ...")
"""
import os
import json
from typing import Dict, Any


class LLMAdapter:
    def __init__(self):
        # Look for common environment variables (do not require these)
        self.openai_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
        # Additional adapters (azure, anthropic, etc.) could be added here

    def is_configured(self) -> bool:
        return bool(self.openai_key)

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> Dict[str, Any]:
        """Generate a response from configured LLM, or return a deterministic stub.

        Returns a dict with keys: text, tokens_used, metadata
        """
        if self.is_configured():
            # Minimal real adapter placeholder: call OpenAI if key exists.
            # We avoid importing openai at module import time so this stays optional.
            try:
                import openai
                openai.api_key = self.openai_key
                resp = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                text = resp.choices[0].text.strip()
                return {"text": text, "tokens_used": resp.usage if hasattr(resp, 'usage') else None, "metadata": {}}
            except Exception as e:
                # If real call fails, return a fallback message but include error in metadata
                return {"text": f"[LLM error fallback] {str(e)}", "tokens_used": None, "metadata": {"error": str(e)}}

        # Deterministic offline stub: echo some structure
        lines = [l.strip() for l in prompt.split('\n') if l.strip()]
        summary = lines[0] if lines else "No prompt"
        stub_text = f"[STUB LLM] Summarized: {summary[:200]}"
        return {"text": stub_text, "tokens_used": 0, "metadata": {"stub": True}}
