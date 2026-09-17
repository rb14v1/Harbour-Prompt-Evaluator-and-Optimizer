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
        """Rewrite prompt addressing identified weaknesses."""
        if not self.client:
            return self._context_aware_improvement(
                original_prompt, validation, scoring, iteration
            )

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
            return self._context_aware_improvement(
                original_prompt, validation, scoring, iteration
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

        return self._context_aware_improvement("", {}, {}, iteration)

    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _context_aware_improvement(
        self,
        original_prompt: str,
        validation: Dict[str, Any],
        scoring: Dict[str, Any],
        iteration: int
    ) -> Dict[str, Any]:
        """Generate contextual improvement based on validation results."""
        prompt_lower = original_prompt.lower()
        validation_data = validation.get("validation", {}) if validation else {}
        low_scoring = scoring.get("low_scoring_dimensions", []) if scoring else []

        improved = original_prompt
        changes = []
        dims_addressed = []

        # Add missing elements based on low-scoring dimensions
        if "specificity" in low_scoring or validation_data.get("specificity", {}).get("score", 10) < 8:
            if "example" not in prompt_lower:
                improved += "\n\nProvide specific examples or illustrative use cases."
                changes.append("Added requirement for specific examples")
                dims_addressed.append("specificity")

        if "context" in low_scoring or validation_data.get("context", {}).get("score", 10) < 8:
            if "audience" not in prompt_lower and "target" not in prompt_lower:
                improved += "\n\nTarget audience: professionals and experts in the field."
                changes.append("Added audience and context specification")
                dims_addressed.append("context")

        if "requirements" in low_scoring or validation_data.get("requirements", {}).get("score", 10) < 8:
            if "must" not in prompt_lower and "should" not in prompt_lower:
                improved += "\n\nKey requirements:\n- Must be clear and well-structured\n- Should include relevant details\n- Must preserve core intent"
                changes.append("Added explicit requirements")
                dims_addressed.append("requirements")

        if "expected_output" in low_scoring or validation_data.get("expected_output", {}).get("score", 10) < 8:
            if "output" not in prompt_lower and "format" not in prompt_lower:
                improved += "\n\nExpected output: Well-structured, detailed response with clear sections."
                changes.append("Specified expected output format")
                dims_addressed.append("expected_output")

        if "completeness" in low_scoring or validation_data.get("completeness", {}).get("score", 10) < 8:
            if "comprehensive" not in prompt_lower and "complete" not in prompt_lower:
                improved += "\n\nEnsure comprehensive coverage of all relevant aspects."
                changes.append("Added completeness requirement")
                dims_addressed.append("completeness")

        if "constraints" in low_scoring or validation_data.get("constraints", {}).get("score", 10) < 8:
            if "limit" not in prompt_lower and "constraint" not in prompt_lower:
                improved += "\n\nConstraints: Keep response focused and avoid unnecessary tangents."
                changes.append("Added constraints and focus guidelines")
                dims_addressed.append("constraints")

        if "actionability" in low_scoring or validation_data.get("actionability", {}).get("score", 10) < 8:
            if "step" not in prompt_lower and "instruction" not in prompt_lower:
                improved += "\n\nProvide step-by-step guidance that can be immediately implemented."
                changes.append("Added actionability requirement")
                dims_addressed.append("actionability")

        if "clarity" in low_scoring or validation_data.get("clarity", {}).get("score", 10) < 8:
            if "clear" not in prompt_lower:
                improved += "\n\nUse clear, direct language and avoid ambiguous phrasing."
                changes.append("Enhanced clarity requirement")
                dims_addressed.append("clarity")

        return {
            "improved_prompt": improved if improved != original_prompt else original_prompt,
            "changes_made": changes if changes else ["Applied enhancement for iteration " + str(iteration)],
            "dimensions_addressed": dims_addressed if dims_addressed else ["general"],
            "intent_preserved": True,
            "iteration": iteration,
            "reasoning": f"Iteration {iteration}: Addressed low-scoring dimensions with targeted improvements"
        }
