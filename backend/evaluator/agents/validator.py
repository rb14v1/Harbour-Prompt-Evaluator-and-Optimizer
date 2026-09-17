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
        """Validate prompt across all 8 dimensions."""
        if not self.client:
            return self._rule_based_validation(processed_prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": self._format_user_message(processed_prompt, analysis)}
                ],
                temperature=0.3,
                max_completion_tokens=3000
            )
            response_text = response.choices[0].message.content
            result = self._parse_response(response_text)
            return result
        except Exception as e:
            return self._rule_based_validation(processed_prompt)

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

                validation = result.get("validation", {})
                for dim in self.DIMENSIONS:
                    if dim not in validation:
                        validation[dim] = self._default_dimension_score()
                    else:
                        dim_data = validation[dim]
                        if "score" in dim_data:
                            score = dim_data["score"]
                            if score not in self.QUALITY_SCORES.values():
                                valid_scores = list(self.QUALITY_SCORES.values())
                                dim_data["score"] = min(valid_scores, key=lambda x: abs(x - score))

                return {
                    "validation": validation,
                    "overall_issues": result.get("overall_issues", []),
                    "improvement_targets": result.get("improvement_targets", [])
                }
        except (json.JSONDecodeError, ValueError):
            pass

        return self._rule_based_validation("")

    def _default_dimension_score(self) -> Dict[str, Any]:
        """Return default dimension score."""
        return {
            "level": "Moderate",
            "score": 5.0,
            "issues": ["Could not evaluate"],
            "evidence": "",
            "recommendation": "Manual review recommended"
        }

    def _rule_based_validation(self, prompt: str = "") -> Dict[str, Any]:
        """Generate validation scores using rule-based analysis with varied scoring."""
        prompt_lower = prompt.lower() if prompt else ""
        word_count = len(prompt.split()) if prompt else 0

        validation = {}

        # CLARITY: Based on length and structure
        if word_count > 25:
            clarity_score = 9.0
        elif word_count > 15:
            clarity_score = 8.0
        elif word_count > 10:
            clarity_score = 7.0
        else:
            clarity_score = 5.5

        validation["clarity"] = {
            "level": self._get_level(clarity_score),
            "score": clarity_score,
            "issues": [] if clarity_score >= 7.5 else ["Could be more explicit"],
            "evidence": f"Prompt has {word_count} words",
            "recommendation": "Good clarity" if clarity_score >= 8.0 else "Add more detail"
        }

        # SPECIFICITY: Based on examples, numbers, concrete terms
        specificity_score = 5.0
        if any(x in prompt_lower for x in ["example", "such as", "for instance", "e.g.", "like"]):
            specificity_score = 9.0
        elif any(x in prompt_lower for x in ["format", "structure", "type", "provide", "specific"]):
            specificity_score = 8.0
        elif word_count > 15:
            specificity_score = 6.5

        validation["specificity"] = {
            "level": self._get_level(specificity_score),
            "score": specificity_score,
            "issues": [] if specificity_score >= 8.0 else ["Needs more specifics"],
            "evidence": "Examples provided" if specificity_score >= 9.0 else "General terms used",
            "recommendation": "Excellent" if specificity_score >= 9.0 else "Add specific examples"
        }

        # CONTEXT: Based on audience, background, scope
        context_score = 5.0
        if any(x in prompt_lower for x in ["audience", "target", "professional", "context", "background", "scope"]):
            context_score = 9.0
        elif any(x in prompt_lower for x in ["user", "reader", "people", "for"]):
            context_score = 7.5
        elif word_count > 15:
            context_score = 6.0

        validation["context"] = {
            "level": self._get_level(context_score),
            "score": context_score,
            "issues": [] if context_score >= 8.0 else ["Context missing"],
            "evidence": "Context defined" if context_score >= 8.0 else "Limited context",
            "recommendation": "Context provided" if context_score >= 8.0 else "Define audience/context"
        }

        # COMPLETENESS: Based on comprehensive, detailed, all-inclusive terms
        completeness_score = 5.0
        if any(x in prompt_lower for x in ["comprehensive", "complete", "all", "detailed", "thorough", "full"]):
            completeness_score = 8.5
        elif any(x in prompt_lower for x in ["step", "instruction", "information", "include", "each"]):
            completeness_score = 7.5
        elif word_count > 20:
            completeness_score = 6.5

        validation["completeness"] = {
            "level": self._get_level(completeness_score),
            "score": completeness_score,
            "issues": [] if completeness_score >= 8.0 else ["Incomplete info"],
            "evidence": "Complete requirements" if completeness_score >= 8.5 else "Partial details",
            "recommendation": "All elements present" if completeness_score >= 8.5 else "Add missing elements"
        }

        # REQUIREMENTS: Based on must, should, ensure, explicit success criteria
        requirements_score = 5.0
        if any(x in prompt_lower for x in ["must", "requirement", "should", "ensure", "criteria", "success"]):
            requirements_score = 9.0
        elif any(x in prompt_lower for x in ["need", "important", "want", "expect"]):
            requirements_score = 7.5
        elif word_count > 12:
            requirements_score = 6.0

        validation["requirements"] = {
            "level": self._get_level(requirements_score),
            "score": requirements_score,
            "issues": [] if requirements_score >= 8.0 else ["Requirements unclear"],
            "evidence": "Requirements explicit" if requirements_score >= 9.0 else "Implied requirements",
            "recommendation": "Clear requirements" if requirements_score >= 9.0 else "Define requirements"
        }

        # CONSTRAINTS: Based on limit, boundary, constraint terms
        constraints_score = 5.0
        if any(x in prompt_lower for x in ["limit", "constraint", "boundary", "maximum", "minimum", "only", "except"]):
            constraints_score = 8.5
        elif any(x in prompt_lower for x in ["avoid", "don't", "not"]):
            constraints_score = 7.0
        elif word_count > 15:
            constraints_score = 5.5

        validation["constraints"] = {
            "level": self._get_level(constraints_score),
            "score": constraints_score,
            "issues": [] if constraints_score >= 7.5 else ["Constraints undefined"],
            "evidence": "Constraints specified" if constraints_score >= 8.0 else "No constraints",
            "recommendation": "Well-defined" if constraints_score >= 8.0 else "Add constraints"
        }

        # EXPECTED OUTPUT: Based on output, return, result, format, structure
        output_score = 5.0
        if any(x in prompt_lower for x in ["output", "return", "result", "format", "structure", "provide", "show"]):
            output_score = 9.0
        elif any(x in prompt_lower for x in ["give", "make", "create", "write"]):
            output_score = 7.5
        elif word_count > 15:
            output_score = 6.0

        validation["expected_output"] = {
            "level": self._get_level(output_score),
            "score": output_score,
            "issues": [] if output_score >= 8.0 else ["Output unclear"],
            "evidence": "Output format clear" if output_score >= 9.0 else "Output implied",
            "recommendation": "Format specified" if output_score >= 9.0 else "Specify output format"
        }

        # ACTIONABILITY: Based on steps, how-to, examples, verbs
        actionability_score = 5.0
        if any(x in prompt_lower for x in ["step", "instruction", "how", "example", "follow", "each"]):
            actionability_score = 9.0
        elif any(x in prompt_lower for x in ["do", "create", "write", "make", "build", "develop"]):
            actionability_score = 8.0
        elif word_count > 12:
            actionability_score = 7.0

        validation["actionability"] = {
            "level": self._get_level(actionability_score),
            "score": actionability_score,
            "issues": [] if actionability_score >= 8.0 else ["Add steps/examples"],
            "evidence": "Actionable format" if actionability_score >= 9.0 else "Can be executed",
            "recommendation": "Highly actionable" if actionability_score >= 9.0 else "Add step-by-step guidance"
        }

        return {
            "validation": validation,
            "overall_issues": ["Rule-based validation applied"],
            "improvement_targets": [d for d in self.DIMENSIONS if validation[d]["score"] < 8.0]
        }

    def _get_level(self, score: float) -> str:
        """Get quality level from score."""
        if score >= 9.0:
            return "Excellent"
        elif score >= 7.5:
            return "Good"
        elif score >= 5.0:
            return "Moderate"
        else:
            return "Poor"
