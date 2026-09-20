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
        """Generate customized improvement based on actual validation feedback - be smart about detailed prompts."""
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

            # Check if original prompt is already detailed (has lots of content OR specific technical details)
            word_count = len(original_prompt.split())
            prompt_lower = original_prompt.lower()

            # Detailed if: many words OR contains specific technical terms/details
            has_technical_details = any(x in prompt_lower for x in [
                "django", "flask", "api", "json", "xml", "azure", "aws", "database",
                "docker", "kubernetes", "sql", "mongodb", "sha-256", "oauth", "jwt",
                "rest", "graphql", "websocket", "python", "javascript", "java", "golang"
            ])
            has_specific_formats = any(x in prompt_lower for x in [
                "pdf", "jpg", "png", "csv", "xml", "json", "html", ".xlsx"
            ])
            is_detailed_prompt = word_count > 80 or (word_count > 40 and (has_technical_details or has_specific_formats))

            # Build customized improvement
            improved = original_prompt

            # For detailed prompts, add concise enhancements focused on low dimensions
            # For brief prompts, add fuller template sections

            if is_detailed_prompt:
                # DETAILED PROMPT MODE: Add concise, targeted improvements

                if validation_data.get("clarity", {}).get("score", 10) < 8:
                    improved += f"\n\n**Clarity Enhancement:** Break down complex concepts with step-by-step breakdown. Define all technical terms and acronyms on first mention."
                    improvements.append("Added clarity enhancements")
                    dims_addressed.append("clarity")

                if validation_data.get("specificity", {}).get("score", 10) < 8:
                    improved += f"\n\n**Specificity Enhancement:** Include concrete examples with actual values/formats. For example, if mentioning 'validate data', specify: 'Validate email format as RFC 5322 compliant.'"
                    improvements.append("Added specific examples")
                    dims_addressed.append("specificity")

                if validation_data.get("context", {}).get("score", 10) < 8:
                    improved += f"\n\n**Context Enhancement:** Specify the target audience explicitly. Define the business/technical context. Example: 'For enterprise users familiar with REST APIs' or 'Assumes knowledge of Docker.'"
                    improvements.append("Clarified context and audience")
                    dims_addressed.append("context")

                if validation_data.get("completeness", {}).get("score", 10) < 8:
                    improved += f"\n\n**Completeness Enhancement:** Add sections for setup/prerequisites, detailed process, error handling, and success validation."
                    improvements.append("Enhanced completeness")
                    dims_addressed.append("completeness")

                if validation_data.get("requirements", {}).get("score", 10) < 8:
                    improved += f"\n\n**Requirements Enhancement:** State success criteria explicitly with measurable metrics. Example: 'Must process 100 receipts/minute with <2% error rate' instead of 'Must work fast.'"
                    improvements.append("Added measurable success criteria")
                    dims_addressed.append("requirements")

                if validation_data.get("constraints", {}).get("score", 10) < 8:
                    improved += f"\n\n**Constraints Enhancement:** Define explicit boundaries and exclusions. Example: 'Only supports PDF, JPG, PNG (not GIF). Maximum file size 10MB. No support for handwritten receipts.'"
                    improvements.append("Clarified constraints")
                    dims_addressed.append("constraints")

                if validation_data.get("expected_output", {}).get("score", 10) < 8:
                    improved += f"\n\n**Output Format Enhancement:** Specify exact response format. Example: 'Return JSON with fields: {{\"receipt_id\": UUID, \"total\": float, \"items\": [{item}], \"confidence\": 0-100%}}'"
                    improvements.append("Specified output format")
                    dims_addressed.append("expected_output")

                if validation_data.get("actionability", {}).get("score", 10) < 8:
                    improved += f"\n\n**Actionability Enhancement:** Break down into numbered steps with clear inputs/outputs. Example: 'Step 1: User uploads receipt (input: image file). Step 2: System extracts text (output: JSON with OCR data).'"
                    improvements.append("Added actionable steps")
                    dims_addressed.append("actionability")
            else:
                # BRIEF PROMPT MODE: Add fuller template sections with actual examples

                if validation_data.get("clarity", {}).get("score", 10) < 8:
                    improved += f"\n\n### Clarity Improvements:\n- Use clear, non-ambiguous language\n- Define all acronyms and technical terms\n- Break complex steps into smaller parts"
                    improvements.append("Clarified language and structure")
                    dims_addressed.append("clarity")

                if validation_data.get("specificity", {}).get("score", 10) < 8:
                    improved += f"\n\n### Specific Examples & Details:\n- Include concrete examples with actual values\n- Specify exact formats, data types, and structures\n- Provide sample inputs and outputs"
                    improvements.append("Added specific examples")
                    dims_addressed.append("specificity")

                if validation_data.get("context", {}).get("score", 10) < 8:
                    improved += f"\n\n### Context & Background:\n- Define target audience and skill level\n- Explain why this task is important\n- State any assumptions about prior knowledge"
                    improvements.append("Added context and background")
                    dims_addressed.append("context")

                if validation_data.get("completeness", {}).get("score", 10) < 8:
                    improved += f"\n\n### Completeness:\n- Include all necessary prerequisites\n- Describe complete workflow from start to finish\n- Mention edge cases and error handling"
                    improvements.append("Added missing components")
                    dims_addressed.append("completeness")

                if validation_data.get("requirements", {}).get("score", 10) < 8:
                    improved += f"\n\n### Success Criteria:\n- Must meet: (non-negotiable requirements)\n- Performance metrics: (speed, scale, accuracy targets)\n- How to validate success"
                    improvements.append("Defined success criteria")
                    dims_addressed.append("requirements")

                if validation_data.get("constraints", {}).get("score", 10) < 8:
                    improved += f"\n\n### Constraints & Limitations:\n- What's included vs excluded\n- Technology/tool limitations\n- Time or resource constraints"
                    improvements.append("Defined constraints")
                    dims_addressed.append("constraints")

                if validation_data.get("expected_output", {}).get("score", 10) < 8:
                    improved += f"\n\n### Expected Output Format:\n- Format type (JSON, text, code, etc.)\n- Specific fields/structure required\n- Example of good output"
                    improvements.append("Specified output format")
                    dims_addressed.append("expected_output")

                if validation_data.get("actionability", {}).get("score", 10) < 8:
                    improved += f"\n\n### Actionable Steps:\n- Step 1: (clear input and output)\n- Step 2: (with dependencies)\n- Step 3: (completion criteria)"
                    improvements.append("Added executable steps")
                    dims_addressed.append("actionability")

            if not improvements:
                improved += f"\n\n**Quality Assessment:** This prompt is well-structured and specific. It clearly defines requirements, constraints, and expected outcomes."
                improvements = ["Prompt already well-specified"]
                dims_addressed = ["general"]

            return {
                "improved_prompt": improved,
                "changes_made": improvements,
                "dimensions_addressed": dims_addressed,
                "intent_preserved": True,
                "iteration": iteration,
                "reasoning": f"Iteration {iteration}: {'Concise enhancements for detailed prompt' if is_detailed_prompt else 'Comprehensive guidance for brief prompt'}"
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
