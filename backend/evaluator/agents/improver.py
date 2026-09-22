import os
import json
from typing import Dict, Any, List
from openai import AzureOpenAI
 
 
class ImproverAgent:
    """
    Intelligently rewrites prompts to address specific low-scoring dimensions.
    Uses Azure OpenAI to generate targeted improvements based on validation analysis.
    """
 
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
        iteration: int = 1,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Intelligently improve a prompt by targeting low-scoring dimensions.
 
        Args:
            original_prompt: The original prompt text
            analysis: Analysis breakdown (intent, requirements, missing_info, ambiguities)
            validation: Validation results with dimension scores and issues
            scoring: Scoring results with low_scoring_dimensions
            iteration: Current iteration number
            metadata: User metadata (role, expertise_level, context)
 
        Returns:
            Dict with improved_prompt, changes_made, dimensions_addressed, intent_preserved
        """
        if metadata is None:
            metadata = {}
 
        # If no Azure client, use fallback rule-based improvement
        if not self.client:
            print("[IMPROVER] Azure unavailable - using fallback heuristics")
            return self._fallback_improvement(original_prompt, validation, scoring, iteration)
 
        try:
            print("[IMPROVER] Generating targeted improvements...")
 
            # Get low-scoring dimensions to focus on
            low_dims = scoring.get("low_scoring_dimensions", [])
 
            # If score is already good enough (>= 9.0 threshold), minimal changes
            overall_score = scoring.get('overall_score', 0)
            if overall_score >= 9.0:
                print("[IMPROVER] Score already above 9.0 - no changes needed")
                return {
                    "improved_prompt": original_prompt,
                    "changes_made": ["Score already meets quality threshold"],
                    "dimensions_addressed": [],
                    "intent_preserved": True,
                    "iteration": iteration,
                    "reasoning": f"Iteration {iteration}: Score {overall_score:.1f} already above threshold"
                }
 
            # Call Azure to generate targeted improvements
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
                            original_prompt, analysis, validation, scoring, metadata
                        )
                    }
                ],
                temperature=0.7,
                max_completion_tokens=3000
            )
 
            response_text = response.choices[0].message.content
            result = self._parse_response(response_text, iteration)
 
            # Verify intent preservation
            if not self._verify_intent(original_prompt, result.get("improved_prompt", ""), analysis):
                print("[IMPROVER] Intent preservation check failed - reverting to fallback")
                return self._fallback_improvement(original_prompt, validation, scoring, iteration)
 
            improved_length = len(result.get("improved_prompt", ""))
            print(f"[IMPROVER] Generated improved prompt: {improved_length} chars, addressing: {result.get('dimensions_addressed', [])}")
            return result
 
        except Exception as e:
            print(f"[IMPROVER] Error during improvement: {str(e)}")
            return self._fallback_improvement(original_prompt, validation, scoring, iteration)
 
    def _get_system_prompt(self) -> str:
        """System prompt for targeted prompt improvement."""
        return """You are a prompt improvement specialist. Your task is to rewrite a prompt to address specific identified weaknesses.
 
CRITICAL RULES:
1. **Target Only Weak Dimensions**: Focus improvements on the dimensions specified as low-scoring (not on already-strong areas)
2. **Preserve Original Intent**: The rewritten prompt must maintain the exact same core objective as the original
3. **Be Specific**: Add concrete details, examples, requirements—not generic boilerplate
4. **Be Domain-Aware**: If the prompt is about Python, add Python-specific context. If about design, design-specific requirements. Etc.
5. **No Templates**: Do NOT use generic sections like "Deliverables" or "Success Criteria" unless they directly address identified gaps
 
Return a valid JSON object with these exact keys:
{
  "improved_prompt": "The rewritten prompt addressing specific weaknesses while preserving intent",
  "changes_made": ["Specific change 1: what was added/modified", "Specific change 2"],
  "dimensions_addressed": ["dimension1", "dimension2"],
  "intent_preserved": true,
  "reasoning": "Brief explanation of improvements made"
}"""
 
    def _format_user_message(
        self,
        original_prompt: str,
        analysis: Dict[str, Any],
        validation: Dict[str, Any],
        scoring: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> str:
        """Format user message with diagnostic data about what needs improvement."""
 
        low_dims = scoring.get("low_scoring_dimensions", [])
        low_dims_text = ", ".join(low_dims) if low_dims else "multiple dimensions"
 
        # Extract key issues from validation
        validation_issues = self._extract_validation_issues(validation, low_dims)
 
        # Extract missing information and ambiguities from analysis
        missing_info = analysis.get("missing_information", [])
        ambiguities = analysis.get("ambiguities", [])
 
        missing_text = "\n".join([f"- {item}" for item in missing_info[:5]])
        ambiguities_text = "\n".join([f"- {item}" for item in ambiguities[:5]])
 
        user_role = metadata.get("user_role", "General")
        expertise = metadata.get("expertise_level", "Intermediate")
 
        return f"""ORIGINAL PROMPT:
========================================
{original_prompt}
========================================
 
IMPROVEMENT CONTEXT:
- Current Score: {scoring.get('overall_score', 0):.1f}/10.0
- Low-Scoring Dimensions: {low_dims_text}
- User Role: {user_role}
- Expertise Level: {expertise}
 
IDENTIFIED GAPS (from validation):
{validation_issues if validation_issues else "No specific issues recorded"}
 
MISSING INFORMATION:
{missing_text if missing_text else "None identified"}
 
AMBIGUITIES TO CLARIFY:
{ambiguities_text if ambiguities_text else "None identified"}
 
YOUR TASK:
Rewrite this prompt to specifically address the low-scoring dimensions ({low_dims_text})
while preserving the original intent. Add concrete details, requirements, and constraints
that were identified as missing. Make it specific to the domain and user's expertise level."""
 
    def _extract_validation_issues(self, validation: Dict[str, Any], low_dims: List[str]) -> str:
        """Extract validation issues for low-scoring dimensions."""
        issues_text = []
        validation_data = validation.get("validation", {})
 
        for dim in low_dims:
            if dim in validation_data:
                data = validation_data[dim]
                level = data.get("level", "Unknown")
                score = data.get("score", 0)
                issues = data.get("issues", [])
                evidence = data.get("evidence", "")
 
                issue_str = f"- {dim.replace('_', ' ').title()} ({level}, {score:.1f}/10): "
                if issues:
                    issue_str += "; ".join(issues[:2])
                elif evidence:
                    issue_str += evidence[:100]
                else:
                    issue_str += "Needs improvement"
 
                issues_text.append(issue_str)
 
        return "\n".join(issues_text) if issues_text else "No specific issues"
 
    def _verify_intent(self, original: str, improved: str, analysis: Dict[str, Any]) -> bool:
        """
        Verify that improved prompt preserves original intent.
        Uses simple heuristics: check for key terms from analysis.
        """
        original_lower = original.lower()
        improved_lower = improved.lower()
 
        # Extract key terms from original prompt
        intent = analysis.get("intent", "").lower()
 
        # Simple check: if original has specific key terms, they should still be in improved
        # or the improved should be significantly longer (means it expanded with context)
        if intent:
            # Intent is preserved if: intent terms are in improved, or improved is >1.3x longer
            key_terms = intent.split()[:3]  # First 3 words of intent
            matching_terms = sum(1 for term in key_terms if term in improved_lower)
 
            if matching_terms >= 2:  # At least 2 of first 3 words of intent preserved
                return True
            elif len(improved) > len(original) * 1.3:  # Significantly expanded
                return True
            else:
                return False
 
        # Default: if improved is longer than original, assume improvement
        return len(improved) > len(original)
 
    def _parse_response(self, response_text: str, iteration: int) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            # Extract JSON block from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
 
            if start_idx == -1 or end_idx <= start_idx:
                raise ValueError("No JSON found in response")
 
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
 
            return {
                "improved_prompt": str(result.get("improved_prompt", "")).strip(),
                "changes_made": self._ensure_list(result.get("changes_made", [])),
                "dimensions_addressed": self._ensure_list(result.get("dimensions_addressed", [])),
                "intent_preserved": bool(result.get("intent_preserved", True)),
                "iteration": iteration,
                "reasoning": str(result.get("reasoning", "Improvements applied"))
            }
 
        except Exception as e:
            print(f"[IMPROVER] Failed to parse response: {str(e)}")
            raise
 
    def _fallback_improvement(
        self,
        original_prompt: str,
        validation: Dict[str, Any],
        scoring: Dict[str, Any],
        iteration: int
    ) -> Dict[str, Any]:
        """
        Intelligent fallback improvement using agent outputs.
        Analyzes validation data to generate targeted improvements.
        """
        improved = original_prompt
        changes = []
        dims_addressed = []

        low_dims = scoring.get("low_scoring_dimensions", [])
        validation_data = validation.get("validation", {})

        # For each low-scoring dimension, add targeted improvement based on validation feedback
        for dim in low_dims:
            if dim in validation_data:
                dim_data = validation_data[dim]
                issues = dim_data.get("issues", [])
                evidence = dim_data.get("evidence", "")

                if dim == "requirements" and "require" not in original_prompt.lower():
                    improvement_text = "\n\nRequirements & Success Criteria:"
                    if issues:
                        improvement_text += f"\n- {issues[0]}" if isinstance(issues, list) else f"\n- {issues}"
                    improvement_text += "\n- Measurable success metrics\n- Performance targets"
                    improved += improvement_text
                    changes.append(f"Added requirements based on: {evidence[:50] if evidence else 'validation feedback'}")
                    dims_addressed.append("requirements")

                elif dim == "constraints" and "constraint" not in original_prompt.lower():
                    improvement_text = "\n\nConstraints & Limitations:"
                    if issues:
                        improvement_text += f"\n- {issues[0]}" if isinstance(issues, list) else f"\n- {issues}"
                    improvement_text += "\n- Scope boundaries\n- Resource limits"
                    improved += improvement_text
                    changes.append(f"Added constraints based on: {evidence[:50] if evidence else 'validation feedback'}")
                    dims_addressed.append("constraints")

                elif dim == "context" and "context" not in original_prompt.lower():
                    improvement_text = "\n\nContext & Background:"
                    if issues:
                        improvement_text += f"\n- {issues[0]}" if isinstance(issues, list) else f"\n- {issues}"
                    improvement_text += "\n- Target audience and skill level\n- Problem domain context"
                    improved += improvement_text
                    changes.append(f"Added context based on: {evidence[:50] if evidence else 'validation feedback'}")
                    dims_addressed.append("context")

                elif dim == "expected_output" and "output" not in original_prompt.lower():
                    improvement_text = "\n\nExpected Output Format:"
                    if issues:
                        improvement_text += f"\n- {issues[0]}" if isinstance(issues, list) else f"\n- {issues}"
                    improvement_text += "\n- Specific format structure\n- Required fields and data types"
                    improved += improvement_text
                    changes.append(f"Added output format based on: {evidence[:50] if evidence else 'validation feedback'}")
                    dims_addressed.append("expected_output")

                elif dim == "clarity":
                    if len(original_prompt.split()) < 50:
                        improved = f"{improved.rstrip()}\n\nClarification: " + ("Provide more specific details. " if issues else "")
                        improved += "Use concrete examples and avoid ambiguous language."
                        changes.append("Added clarity guidance")
                        dims_addressed.append("clarity")

                elif dim == "specificity":
                    specificity_boost = "\n\nSpecificity Enhancements:\n- Include concrete examples\n- Use specific tool/framework names\n- Add measurable metrics"
                    improved += specificity_boost
                    changes.append("Enhanced specificity with concrete examples")
                    dims_addressed.append("specificity")

                elif dim == "actionability":
                    actionability_boost = "\n\nActionability Steps:\n1. Clear starting point\n2. Defined intermediate steps\n3. Measurable end goal\n4. Success validation method"
                    improved += actionability_boost
                    changes.append("Added actionable step structure")
                    dims_addressed.append("actionability")

                elif dim == "completeness":
                    if issues:
                        completeness_boost = f"\n\nMissing Elements: {issues[0] if isinstance(issues, list) else issues}"
                        improved += completeness_boost
                    changes.append("Flagged completeness gaps")
                    dims_addressed.append("completeness")

        if not changes:
            changes = ["Analyzed but prompt already covers key areas"]

        return {
            "improved_prompt": improved,
            "changes_made": changes,
            "dimensions_addressed": dims_addressed if dims_addressed else ["general"],
            "intent_preserved": True,
            "iteration": iteration,
            "reasoning": f"Iteration {iteration}: Intelligent fallback using validation data"
        }
 
    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)] if value else []
 
 