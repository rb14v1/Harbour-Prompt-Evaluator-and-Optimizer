import os
import json
import logging
import random
import time
from typing import Dict, Any, Optional
from ..exceptions import LLMException

logger = logging.getLogger(__name__)

class LLMClient:
    RATE_LIMIT_MAX_ATTEMPTS = 6

    """
    Unified client for Azure OpenAI / OpenAI interactions.
    Supports Azure OpenAI credentials from environment variables:
      - AZURE_OPENAI_ENDPOINT
      - AZURE_OPENAI_API_KEY
      - AZURE_OPENAI_DEPLOYMENT or AZURE_OPENAI_MODEL
      - AZURE_OPENAI_API_VERSION
    Falls back gracefully to intelligent deterministic mock logic if API credentials are not configured,
    ensuring robust operation in all environments.
    """

    def __init__(self):
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", os.getenv("AZURE_OPENAI_MODEL", "")).strip()
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview").strip()

        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o").strip()

        self.client = None
        self.is_azure = False

        # Ignore sample / placeholder keys from .env.example
        is_placeholder_azure = (
            "your-resource-name" in self.azure_endpoint
            or "your-azure-api-key" in self.azure_api_key
            or not self.azure_api_key
            or not self.azure_endpoint
        )
        is_placeholder_openai = (
            "sk-..." in self.openai_api_key
            or "your-openai-api-key" in self.openai_api_key
            or not self.openai_api_key
        )

        if not is_placeholder_azure:
            try:
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    azure_endpoint=self.azure_endpoint,
                    api_key=self.azure_api_key,
                    api_version=self.azure_api_version,
                )
                self.is_azure = True
                logger.info("Initialized AzureOpenAI client successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize AzureOpenAI client: {e}")
        elif not is_placeholder_openai:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_api_key)
                self.is_azure = False
                logger.info("Initialized OpenAI client successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
        else:
            logger.info("No active LLM API keys provided. LLMClient will operate in intelligent fallback generation mode.")

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2, json_mode: bool = False, max_retries: int = 2) -> str:
        if not self.is_configured():
            logger.debug("LLM client not configured, returning empty response")
            return ""

        model_or_deployment = self.azure_deployment if self.is_azure else self.openai_model
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        attempt = 0
        while True:
            attempt += 1
            try:
                kwargs: Dict[str, Any] = {
                    "model": model_or_deployment,
                    "messages": messages,
                    "temperature": temperature,
                    "timeout": 120.0,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                logger.debug(f"LLM API call attempt {attempt} with model {model_or_deployment}")
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content or ""

                logger.debug(f"LLM call successful, response length: {len(content)}")
                return content.strip()

            except Exception as e:
                error_msg = str(e)
                is_rate_limit = "429" in error_msg or "rate_limit" in error_msg.lower()
                max_attempts = self.RATE_LIMIT_MAX_ATTEMPTS if is_rate_limit else max_retries
                is_last_attempt = attempt >= max_attempts
                log_level = logging.ERROR if is_last_attempt else logging.WARNING

                logger.log(
                    log_level,
                    f"LLM API error (attempt {attempt}/{max_attempts}): {error_msg}",
                    exc_info=True
                )

                if is_last_attempt:
                    logger.error(f"LLM call failed after {attempt} attempts")
                    return ""

                if is_rate_limit:
                    wait_time = self._rate_limit_wait(e, attempt)
                else:
                    wait_time = 2 ** (attempt - 1)  # Exponential backoff: 1s, 2s, 4s...
                logger.debug(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)

    def _rate_limit_wait(self, error: Exception, attempt: int) -> float:
        retry_after = None
        headers = getattr(getattr(error, "response", None), "headers", None) or {}
        try:
            retry_after = float(headers.get("retry-after"))
        except (TypeError, ValueError):
            pass
        backoff = min(2 ** attempt, 30)
        return max(retry_after or 0.0, backoff) + random.uniform(0, 1)

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Optional[Dict[str, Any]]:
        raw_text = self.generate_chat(system_prompt, user_prompt, temperature=temperature, json_mode=True)
        if not raw_text:
            logger.debug("No response from LLM")
            return None

        try:
            # Strip markdown json blocks if returned
            clean = raw_text.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()

            # Parse JSON
            parsed = json.loads(clean)

            if not isinstance(parsed, dict):
                logger.warning(f"LLM returned non-dict JSON: {type(parsed).__name__}")
                return None

            logger.debug(f"Successfully parsed JSON with keys: {list(parsed.keys())}")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {str(e)}")
            logger.debug(f"Raw response (first 500 chars): {raw_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing LLM JSON: {str(e)}", exc_info=True)
            return None


# Global singleton instance
llm_client = LLMClient()
