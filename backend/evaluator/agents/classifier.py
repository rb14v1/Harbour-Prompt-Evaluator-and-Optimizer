import os
import json
from typing import Dict, Any
from openai import AzureOpenAI

class ClassifierAgent:
    """
    Classifies prompts by task type and complexity.
    """

    TASK_CATEGORIES = [
        "Create Content",
        "Create Code",
        "Research",
        "Deep Research / Analysis",
        "Plan and Organize",
        "Ideate",
        "Summarize",
        "Explain",
        "Optimize"
    ]

    COMPLEXITY_LEVELS = ["Simple", "Moderate", "Complex"]

    def __init__(self):
        self.name = "Classifier Agent"
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

    def classify(self, processed_prompt: str) -> Dict[str, Any]:
        """
        Classify prompt into task category and assess complexity.

        Args:
            processed_prompt: Normalized prompt text

        Returns:
            Classification with task type, complexity, confidence, and reasoning
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": f"Classify this prompt:\n\n{processed_prompt}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            response_text = response.choices[0].message.content
            result = self._parse_response(response_text)
            return result

        except Exception as e:
            return {
                "task_type": "Unknown",
                "complexity": "Moderate",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}"
            }

    def _get_system_prompt(self) -> str:
        """Return system prompt for classification."""
        categories = ", ".join(self.TASK_CATEGORIES)
        complexity = ", ".join(self.COMPLEXITY_LEVELS)

        return f"""You are a prompt classifier. Classify the given prompt into ONE of these categories:
{categories}

Also assess complexity: {complexity}

Return JSON with fields: task_type, complexity, confidence (0.0-1.0), reasoning

Example output:
{{"task_type": "Create Code", "complexity": "Moderate", "confidence": 0.92, "reasoning": "Request to write a sorting function with specific requirements."}}"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                # Validate and ensure correct structure
                result['confidence'] = max(0.0, min(1.0, float(result.get('confidence', 0.5))))
                result['task_type'] = result.get('task_type', 'Unknown')
                result['complexity'] = result.get('complexity', 'Moderate')
                result['reasoning'] = result.get('reasoning', 'Classification completed')

                return result
        except (json.JSONDecodeError, ValueError):
            pass

        return {
            "task_type": "Unknown",
            "complexity": "Moderate",
            "confidence": 0.5,
            "reasoning": "Could not parse classification response"
        }
