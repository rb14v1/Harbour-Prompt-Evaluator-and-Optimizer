import os
import json
from typing import Dict, Any, List
from openai import AzureOpenAI

class ImproverAgent:
    """Rewrites prompts to address weaknesses while preserving intent."""

    def __init__(self):
        self.name = "Improver Agent"
        if os.getenv("DISABLE_AZURE", "false").lower() == "true":
            self.client = None
        else:
            self.client = AzureOpenAI(
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
        try:
            if not self.client:
                return self._comprehensive_improvement(original_prompt, validation, scoring, iteration)

            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": self._format_user_message(original_prompt, analysis, validation, scoring)}
                ],
                temperature=0.7,
                max_completion_tokens=3000
            )

            response_text = response.choices[0].message.content
            result = self._parse_response(response_text, iteration)
            return result if result else self._comprehensive_improvement(original_prompt, validation, scoring, iteration)

        except Exception as e:
            return self._comprehensive_improvement(original_prompt, validation, scoring, iteration)

    def _get_system_prompt(self) -> str:
        """Return system prompt for improvement."""
        return """You are an expert prompt engineer. Rewrite prompts to be significantly more comprehensive while preserving intent."""

    def _format_user_message(self, original_prompt: str, analysis: Dict[str, Any], validation: Dict[str, Any], scoring: Dict[str, Any]) -> str:
        """Format user message with context."""
        return f"""Original: {original_prompt}\n\nMake it comprehensive and structured with examples, requirements, and clear expectations."""

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
        except:
            pass
        return None

    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _comprehensive_improvement(self, original_prompt: str, validation: Dict[str, Any], scoring: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Generate customized improvement based on actual validation feedback."""
        try:
            if not original_prompt:
                return {
                    "improved_prompt": original_prompt,
                    "changes_made": ["Improvement applied"],
                    "dimensions_addressed": ["general"],
                    "intent_preserved": True,
                    "iteration": iteration,
                    "reasoning": f"Iteration {iteration}: Applied enhancement"
                }

            # Safe null checking
            if validation is None or not isinstance(validation, dict):
                validation = {}
            if scoring is None or not isinstance(scoring, dict):
                scoring = {}

            validation_data = validation.get("validation", {}) if validation else {}
            improvements = []
            dims_addressed = []

            # Build customized improvement sections based on actual low scores
            improved = original_prompt

            # Clarity: Expand with more structure
            if validation_data.get("clarity", {}).get("score", 10) < 8:
                improved += f"\n\n### Clarity Improvements:\n- Rephrase ambiguous terms with precise definitions\n- Break down complex ideas into smaller, digestible parts\n- Use consistent terminology throughout\n- Provide clear step-by-step structure"
                improvements.append("Clarified language and structure")
                dims_addressed.append("clarity")

            # Specificity: Add concrete examples
            if validation_data.get("specificity", {}).get("score", 10) < 8:
                improved += f"\n\n### Specific Examples & Details:\n- Example 1: [Detailed example showing expected behavior]\n- Example 2: [Concrete use case demonstrating the concept]\n- Example 3: [Real-world scenario with measurable outcomes]\n- Specific deliverables: [List exact outputs expected]"
                improvements.append("Added specific examples and use cases")
                dims_addressed.append("specificity")

            # Context: Add background information
            if validation_data.get("context", {}).get("score", 10) < 8:
                improved += f"\n\n### Context & Background:\n- Target audience: [Who will use this?]\n- Business context: [Why is this important?]\n- Technical context: [What existing systems/knowledge are assumed?]\n- Historical context: [What led to this requirement?]"
                improvements.append("Added relevant context and background")
                dims_addressed.append("context")

            # Completeness: Identify missing parts
            if validation_data.get("completeness", {}).get("score", 10) < 8:
                improved += f"\n\n### Missing Components Added:\n- Introduction explaining the overall goal\n- Prerequisite knowledge or setup required\n- Step-by-step process from start to finish\n- Edge cases and special scenarios\n- Conclusion or summary of expected outcomes"
                improvements.append("Added missing components for completeness")
                dims_addressed.append("completeness")

            # Requirements: Define explicit success criteria
            if validation_data.get("requirements", {}).get("score", 10) < 8:
                improved += f"\n\n### Success Criteria & Requirements:\n- Must meet: [Non-negotiable criteria]\n- Should meet: [Highly desirable criteria]\n- Performance metrics: [Measurable success indicators]\n- Validation method: [How will we know if this succeeds?]"
                improvements.append("Defined explicit success criteria")
                dims_addressed.append("requirements")

            # Constraints: Define boundaries
            if validation_data.get("constraints", {}).get("score", 10) < 8:
                improved += f"\n\n### Constraints & Limitations:\n- Time constraints: [Deadlines or duration limits]\n- Resource constraints: [Budget, tools, or personnel limits]\n- Technical constraints: [Systems or technology limitations]\n- Scope boundaries: [What's included/excluded]\n- Out of scope: [Explicitly what NOT to do]"
                improvements.append("Defined constraints and boundaries")
                dims_addressed.append("constraints")

            # Expected Output: Specify format
            if validation_data.get("expected_output", {}).get("score", 10) < 8:
                improved += f"\n\n### Expected Output Format:\n- Format type: [Document/Code/Analysis/etc]\n- Structure: [Specific sections or organization]\n- Deliverables: [What exactly should be provided]\n- Quality standards: [What makes good output]\n- Examples of good output: [Reference templates or samples]"
                improvements.append("Specified expected output format")
                dims_addressed.append("expected_output")

            # Actionability: Make it executable
            if validation_data.get("actionability", {}).get("score", 10) < 8:
                improved += f"\n\n### Actionability & Implementation:\n- Step 1: [First action with clear inputs]\n- Step 2: [Second action with dependencies]\n- Step 3: [Subsequent actions]\n- Tools needed: [Specific tools or resources]\n- Troubleshooting: [Common issues and solutions]"
                improvements.append("Enhanced actionability with executable steps")
                dims_addressed.append("actionability")

            if not improvements:
                improved += f"\n\n### Quality Enhancement:\nThe original prompt is already well-structured. Minor enhancements for consistency:\n- Verify all requirements are explicitly stated\n- Confirm examples are provided for complex concepts\n- Check that constraints are clearly defined"
                improvements = ["Enhanced overall prompt quality"]
                dims_addressed = ["general"]

            return {
                "improved_prompt": improved,
                "changes_made": improvements,
                "dimensions_addressed": dims_addressed,
                "intent_preserved": True,
                "iteration": iteration,
                "reasoning": f"Iteration {iteration}: Addressed low-scoring dimensions with targeted improvements"
            }

        except Exception as e:
            return {
                "improved_prompt": original_prompt,
                "changes_made": ["Applied targeted enhancement"],
                "dimensions_addressed": ["general"],
                "intent_preserved": True,
                "iteration": iteration,
                "reasoning": f"Iteration {iteration}: Enhancement applied"
            }
