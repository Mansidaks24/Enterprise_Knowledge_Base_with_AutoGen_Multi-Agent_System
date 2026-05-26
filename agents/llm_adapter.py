"""
llm_adapter.py

Modern Gemini adapter using google-genai SDK.
"""

import os

from typing import Dict, Any

from dotenv import load_dotenv

from google.generativeai import genai


load_dotenv()


class LLMAdapter:

    def __init__(self):

        self.gemini_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if self.gemini_key:

            self.client = genai.Client(
                api_key=self.gemini_key
            )

        else:

            self.client = None

        self.model = (
            "gemini-1.5-flash"
        )

    # ======================================
    # CHECK CONFIG
    # ======================================

    def is_configured(self):

        return self.client is not None

    # ======================================
    # GENERATE RESPONSE
    # ======================================

    def generate(

        self,

        prompt: str,

        max_tokens: int = 256,

        temperature: float = 0.2

    ) -> Dict[str, Any]:

        # ==================================
        # OFFLINE STUB
        # ==================================

        if not self.is_configured():

            return {

                "text":
                    "[STUB MODE] Gemini not configured.",

                "tokens_used":
                    0,

                "metadata": {

                    "stub": True
                }
            }

        # ==================================
        # GEMINI GENERATION
        # ==================================

        try:

            response = self.client.models.generate_content(

                model=self.model,

                contents=prompt
            )

            text = response.text

            return {

                "text":
                    text,

                "tokens_used":
                    None,

                "metadata": {

                    "provider":
                        "Gemini",

                    "model":
                        self.model
                }
            }

        except Exception as e:

            return {

                "text":
                    f"[Gemini Error] {str(e)}",

                "tokens_used":
                    None,

                "metadata": {

                    "error":
                        str(e)
                }
            }