import os
import json
from typing import Dict, Any, List
from openai import AzureOpenAI

class AnalyzerAgent:
    """
    Decomposes prompts into key components (intent, requirements, context, constraints, etc.)
    """

    def __init__(self):
        self.name = "Analyzer Agent"
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

    def analyze(self, processed_prompt: str, task_type: str = None) -> Dict[str, Any]:
        """
        Analyze and decompose prompt into key components.

        Args:
            processed_prompt: Normalized prompt text
            task_type: Optional task category for context-aware analysis

        Returns:
            Analysis with intent, requirements, context, constraints, expected output, etc.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(task_type)
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this prompt:\n\n{processed_prompt}"
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )

            response_text = response.choices[0].message.content
            result = self._parse_response(response_text)
            return result

        except Exception as e:
            return self._default_analysis(f"Analysis failed: {str(e)}")

    def _get_system_prompt(self, task_type: str = None) -> str:
        """Return system prompt for analysis."""
        task_context = f"Task type: {task_type}" if task_type else ""

        return f"""You are a prompt analyzer. Decompose the given prompt into components.

{task_context}

Extract and return JSON with these fields:
- intent: primary goal (one sentence)
- requirements: list of specific requirements
- context: list of relevant background information
- constraints: list of limitations or boundaries
- expected_output: description of desired output format/structure
- missing_information: list of gaps or unclear information
- ambiguities: list of ambiguous phrases or concepts

Example output:
{{
  "intent": "Write a Python function that sorts arrays",
  "requirements": ["Accept list of integers", "Return sorted list", "Use specific algorithm"],
  "context": ["For educational purposes"],
  "constraints": ["Must be O(n log n) or better"],
  "expected_output": "Python function with docstring",
  "missing_information": ["Should handle duplicates?"],
  "ambiguities": ["What sorting order? (ascending assumed)"]
}}"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                # Ensure all fields are present
                return {
                    "intent": str(result.get("intent", "Analysis completed")),
                    "requirements": self._ensure_list(result.get("requirements", [])),
                    "context": self._ensure_list(result.get("context", [])),
                    "constraints": self._ensure_list(result.get("constraints", [])),
                    "expected_output": str(result.get("expected_output", "")),
                    "missing_information": self._ensure_list(result.get("missing_information", [])),
                    "ambiguities": self._ensure_list(result.get("ambiguities", []))
                }
        except (json.JSONDecodeError, ValueError):
            pass

        return self._default_analysis("Could not parse analysis response")

    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _default_analysis(self, reason: str = "") -> Dict[str, Any]:
        """Return default analysis structure."""
        return {
            "intent": reason or "Analysis incomplete",
            "requirements": [],
            "context": [],
            "constraints": [],
            "expected_output": "",
            "missing_information": ["Full analysis could not be completed"],
            "ambiguities": []
        }
