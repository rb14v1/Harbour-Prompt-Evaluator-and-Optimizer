import os
import json
from typing import Dict, Any, List
from openai import AzureOpenAI

class ImproverAgent:
    """
    Rewrites prompts to address weaknesses while preserving intent.
    """

    def __init__(self):
        self.name = "Improver Agent"
        if os.getenv("DISABLE_AZURE", "false").lower() == "true": self.client = None
        else: self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

    def improve(
        self,
        original_prompt: str,
        analysis: Dict[str, Any],
        validation: Dict[str, Any],
        scoring: Dict[str, Any],
        iteration: int = 1
    ) -> Dict[str, Any]:
        """
        Rewrite prompt addressing identified weaknesses.

        Args:
            original_prompt: Original prompt text
            analysis: Analysis results
            validation: Validation results
            scoring: Scoring results
            iteration: Current iteration number

        Returns:
            Improved prompt with changes documented
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
                        "content": self._format_user_message(
                            original_prompt, analysis, validation, scoring
                        )
                    }
                ],
                temperature=0.3,
                max_completion_tokens=2000
            )

            response_text = response.choices[0].message.content
            result = self._parse_response(response_text, iteration)
            return result

        except Exception as e:
            return self._default_improvement(
                original_prompt, iteration, f"Improvement failed: {str(e)}"
            )

    def _get_system_prompt(self) -> str:
        """Return system prompt for improvement."""
        return """You are a prompt improvement expert. Your task is to rewrite the given prompt to address identified weaknesses while STRICTLY preserving the original intent.

Guidelines:
1. Focus on lowest-scoring dimensions first
2. Add specific details, clarify ambiguities
3. Define constraints, requirements, and output format clearly
4. Preserve original intent completely - do not change what the user wants
5. Document each change made and why

Return JSON with:
{
  "improved_prompt": "revised prompt addressing weaknesses",
  "changes_made": ["change 1 with reasoning", "change 2 with reasoning"],
  "dimensions_addressed": ["dimension1", "dimension2"],
  "intent_preserved": true/false,
  "reasoning": "brief explanation of strategy"
}

If you cannot preserve intent while addressing issues, set intent_preserved to false and explain the conflict."""

    def _format_user_message(
        self,
        original_prompt: str,
        analysis: Dict[str, Any],
        validation: Dict[str, Any],
        scoring: Dict[str, Any]
    ) -> str:
        """Format user message with context."""
        low_dims = scoring.get("low_scoring_dimensions", [])
        low_dims_text = ", ".join(low_dims) if low_dims else "all dimensions"

        return f"""Original Prompt:
{original_prompt}

Current Score: {scoring.get('overall_score', 'Unknown')}/10.0
Threshold: {scoring.get('threshold', 7.0)}
Status: {scoring.get('status', 'Unknown')}

Lowest-Scoring Dimensions to Focus On:
{low_dims_text}

Analysis Summary:
- Intent: {analysis.get('intent', 'Unknown')}
- Missing Information: {', '.join(analysis.get('missing_information', []))}
- Ambiguities: {', '.join(analysis.get('ambiguities', []))}

Validation Issues:
{self._format_validation_issues(validation)}

Your Task:
Rewrite the prompt to address the low-scoring dimensions while preserving the original intent. Make it clearer, more specific, and more actionable."""

    def _format_validation_issues(self, validation: Dict[str, Any]) -> str:
        """Format validation issues for display."""
        issues_text = []
        validation_data = validation.get("validation", {})

        for dim, data in validation_data.items():
            if isinstance(data, dict):
                level = data.get("level", "Unknown")
                issue_list = data.get("issues", [])
                if issue_list:
                    issues_text.append(f"- {dim.capitalize()} ({level}): {', '.join(issue_list[:2])}")

        return "\n".join(issues_text) if issues_text else "No specific issues recorded"

    def _parse_response(self, response_text: str, iteration: int) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                return {
                    "improved_prompt": str(result.get("improved_prompt", "")),
                    "changes_made": self._ensure_list(result.get("changes_made", [])),
                    "dimensions_addressed": self._ensure_list(result.get("dimensions_addressed", [])),
                    "intent_preserved": bool(result.get("intent_preserved", True)),
                    "iteration": iteration,
                    "reasoning": str(result.get("reasoning", ""))
                }
        except (json.JSONDecodeError, ValueError):
            pass

        return self._default_improvement("", iteration, "Could not parse improvement response")

    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _default_improvement(
        self, original_prompt: str, iteration: int, reason: str = ""
    ) -> Dict[str, Any]:
        """Return default improvement structure."""
        return {
            "improved_prompt": original_prompt,
            "changes_made": [reason or "Could not generate improvements"],
            "dimensions_addressed": [],
            "intent_preserved": True,
            "iteration": iteration,
            "reasoning": "Improvement incomplete - using original prompt"
        }
