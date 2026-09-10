import os
import json
from typing import Dict, Any
from openai import AzureOpenAI

class ValidatorAgent:
    """
    Evaluates prompts across 8 validation dimensions.
    """

    DIMENSIONS = [
        "clarity",
        "specificity",
        "context",
        "completeness",
        "requirements",
        "constraints",
        "expected_output",
        "actionability"
    ]

    QUALITY_LEVELS = ["Poor", "Moderate", "Good", "Excellent"]
    QUALITY_SCORES = {
        "Poor": 2.5,
        "Moderate": 5.0,
        "Good": 7.5,
        "Excellent": 10.0
    }

    def __init__(self):
        self.name = "Validator Agent"
        if os.getenv("DISABLE_AZURE", "false").lower() == "true": self.client = None
        else: self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

    def validate(self, processed_prompt: str, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate prompt across all 8 dimensions.

        Args:
            processed_prompt: Normalized prompt text
            analysis: Optional analysis results from Analyzer

        Returns:
            Validation results with dimension scores and issues
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
                        "content": self._format_user_message(processed_prompt, analysis)
                    }
                ],
                temperature=0.3,
                max_completion_tokens=3000
            )

            response_text = response.choices[0].message.content
            result = self._parse_response(response_text)
            return result

        except Exception as e:
            return self._default_validation(f"Validation failed: {str(e)}")

    def _get_system_prompt(self) -> str:
        """Return system prompt for validation."""
        dimensions = "\n".join([f"- {d.capitalize()}" for d in self.DIMENSIONS])
        quality_levels = ", ".join(self.QUALITY_LEVELS)

        return f"""You are a prompt quality validator. Evaluate prompts across 8 dimensions.

Dimensions to evaluate:
{dimensions}

For each dimension, rate it as: {quality_levels}

Return JSON with structure:
{{
  "validation": {{
    "clarity": {{"level": "Good", "score": 7.5, "issues": ["list"], "evidence": "quote", "recommendation": "text"}},
    "specificity": {{...}},
    ... (8 dimensions total)
  }},
  "overall_issues": ["summary list"],
  "improvement_targets": ["dimension1", "dimension2"]
}}

Score mapping:
- Excellent = 10.0
- Good = 7.5
- Moderate = 5.0
- Poor = 2.5

Provide specific evidence from the prompt for each rating."""

    def _format_user_message(self, prompt: str, analysis: Dict = None) -> str:
        """Format user message with prompt and optional analysis."""
        msg = f"Validate this prompt:\n\n{prompt}\n\n"
        if analysis:
            msg += f"Previous analysis:\n{json.dumps(analysis, indent=2)}\n\n"
        msg += "Evaluate across all 8 dimensions."
        return msg

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                # Validate dimension scores
                validation = result.get("validation", {})
                for dim in self.DIMENSIONS:
                    if dim not in validation:
                        validation[dim] = self._default_dimension_score()
                    else:
                        # Ensure score is valid
                        dim_data = validation[dim]
                        if "score" in dim_data:
                            score = dim_data["score"]
                            if score not in self.QUALITY_SCORES.values():
                                # Round to nearest valid score
                                valid_scores = list(self.QUALITY_SCORES.values())
                                dim_data["score"] = min(valid_scores, key=lambda x: abs(x - score))

                return {
                    "validation": validation,
                    "overall_issues": result.get("overall_issues", []),
                    "improvement_targets": result.get("improvement_targets", [])
                }
        except (json.JSONDecodeError, ValueError):
            pass

        return self._default_validation("Could not parse validation response")

    def _default_dimension_score(self) -> Dict[str, Any]:
        """Return default dimension score."""
        return {
            "level": "Moderate",
            "score": 5.0,
            "issues": ["Could not evaluate"],
            "evidence": "",
            "recommendation": "Manual review recommended"
        }

    def _default_validation(self, reason: str = "") -> Dict[str, Any]:
        """Return default validation structure."""
        validation = {}
        for dim in self.DIMENSIONS:
            validation[dim] = self._default_dimension_score()

        return {
            "validation": validation,
            "overall_issues": [reason or "Validation incomplete"],
            "improvement_targets": self.DIMENSIONS
        }
