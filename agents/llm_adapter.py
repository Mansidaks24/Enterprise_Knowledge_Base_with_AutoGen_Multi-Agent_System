"""
llm_adapter.py

LLM Adapter - supports multiple providers
Primary: Groq (fast, free, no quota issues)
Fallback: Google Gemini
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Try Groq first
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Fallback to Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMAdapter:

    def __init__(self):

        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Try Groq first (preferred)
        if self.groq_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=self.groq_key)
                self.provider = "Groq"
                self.is_available = True
            except Exception as e:
                print(f"Warning: Groq init failed: {e}")
                self.provider = None
                self.is_available = False
                self.client = None
        
        # Fallback to Gemini
        elif self.gemini_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.gemini_key)
                self.client = genai
                self.provider = "Gemini"
                self.is_available = True
            except Exception as e:
                print(f"Warning: Gemini init failed: {e}")
                self.provider = None
                self.is_available = False
                self.client = None
        
        else:
            self.client = None
            self.is_available = False
            self.provider = None

        # Model config based on provider
        if self.provider == "Groq":
            self.model = "llama-3.3-70b-versatile"
        elif self.provider == "Gemini":
            self.model = "gemini-pro"
        else:
            self.model = None

    # ======================================
    # CHECK CONFIG
    # ======================================

    def is_configured(self):

        return self.is_available

    # ======================================
    # GENERATE RESPONSE
    # ======================================

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate a response using the configured LLM provider.
        
        Primary: Groq (fast, free, no quotas)
        Fallback: Gemini
        Fallback: Stub mode (offline)
        """

        # ==================================
        # OFFLINE STUB
        # ==================================

        if not self.is_configured():
            return {
                "text": "[STUB MODE] No LLM configured. Add GROQ_API_KEY or GEMINI_API_KEY to .env",
                "tokens_used": 0,
                "metadata": {"stub": True}
            }

        # ==================================
        # GROQ GENERATION
        # ==================================

        if self.provider == "Groq":
            try:
                message = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                text = message.choices[0].message.content
                return {
                    "text": text,
                    "tokens_used": None,
                    "metadata": {
                        "provider": "Groq",
                        "model": self.model,
                        "speed": "Very Fast ⚡"
                    }
                }
            except Exception as e:
                return {
                    "text": f"[Groq Error] {str(e)}",
                    "tokens_used": None,
                    "metadata": {"error": str(e)}
                }

        # ==================================
        # GEMINI GENERATION
        # ==================================

        elif self.provider == "Gemini":
            try:
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(prompt)
                text = response.text
                return {
                    "text": text,
                    "tokens_used": None,
                    "metadata": {
                        "provider": "Gemini",
                        "model": self.model
                    }
                }
            except Exception as e:
                return {
                    "text": f"[Gemini Error] {str(e)}",
                    "tokens_used": None,
                    "metadata": {"error": str(e)}
                }

        else:
            return {
                "text": "[ERROR] No provider available",
                "tokens_used": None,
                "metadata": {"error": "No provider"}
            }