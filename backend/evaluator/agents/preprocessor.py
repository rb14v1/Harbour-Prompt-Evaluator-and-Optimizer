import uuid
from datetime import datetime
from typing import Dict, Any

class PreprocessorAgent:
    """
    Normalizes input prompt and structures it for downstream processing.
    """

    def __init__(self):
        self.name = "Preprocessor Agent"

    def process(self, raw_prompt: str) -> Dict[str, Any]:
        """
        Process raw prompt into structured format.

        Args:
            raw_prompt: Raw natural language prompt from user

        Returns:
            Structured prompt object with metadata
        """
        return {
            "prompt_id": str(uuid.uuid4()),
            "original_prompt": raw_prompt,
            "processed_prompt": self._normalize(raw_prompt),
            "metadata": {
                "length": len(raw_prompt.split()),
                "timestamp": datetime.utcnow().isoformat(),
                "version": 1
            }
        }

    def _normalize(self, text: str) -> str:
        """Normalize whitespace and basic formatting."""
        # Remove extra whitespace
        normalized = ' '.join(text.split())
        return normalized.strip()
