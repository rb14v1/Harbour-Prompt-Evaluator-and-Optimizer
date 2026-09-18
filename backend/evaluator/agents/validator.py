import os
import json
from typing import Dict, Any
from openai import AzureOpenAI

class ValidatorAgent:
    """Evaluates prompts across 8 validation dimensions."""

    DIMENSIONS = ["clarity", "specificity", "context", "completeness", "requirements", "constraints", "expected_output", "actionability"]
    QUALITY_LEVELS = ["Poor", "Moderate", "Good", "Excellent"]
    QUALITY_SCORES = {"Poor": 2.5, "Moderate": 5.0, "Good": 7.5, "Excellent": 10.0}

    def __init__(self):
        self.name = "Validator Agent"
        if os.getenv("DISABLE_AZURE", "false").lower() == "true":
            self.client = None
        else:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

    def validate(self, processed_prompt: str, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate prompt across all 8 dimensions."""
        if not self.client:
            return self._analyze_prompt_content(processed_prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": f"Validate this prompt:\n\n{processed_prompt}"}
                ],
                temperature=0.3,
                max_completion_tokens=2000
            )
            response_text = response.choices[0].message.content
            result = self._parse_response(response_text)
            return result if result else self._analyze_prompt_content(processed_prompt)
        except Exception as e:
            return self._analyze_prompt_content(processed_prompt)

    def _get_system_prompt(self) -> str:
        return f"""You are a prompt quality validator. Rate each dimension on a scale of 2.5-10.0:
- Poor (2.5): Major gaps
- Moderate (5.0): Some issues
- Good (7.5): Minor improvements possible
- Excellent (10.0): Exemplary

Return JSON with validation scores for: clarity, specificity, context, completeness, requirements, constraints, expected_output, actionability"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                validation = {}
                for dim in self.DIMENSIONS:
                    score = result.get(dim, 5.0)
                    if isinstance(score, str):
                        score = float(score) if score.replace('.', '', 1).isdigit() else 5.0
                    validation[dim] = {
                        "level": self._get_level(score),
                        "score": min(10.0, max(2.5, float(score))),
                        "issues": [],
                        "evidence": "",
                        "recommendation": ""
                    }

                return {
                    "validation": validation,
                    "overall_issues": [],
                    "improvement_targets": [d for d in self.DIMENSIONS if validation[d]["score"] < 8.0]
                }
        except:
            pass
        return None

    def _analyze_prompt_content(self, prompt: str) -> Dict[str, Any]:
        """Analyze actual prompt content to assign meaningful scores."""
        prompt_lower = prompt.lower()
        words = prompt.split()
        word_count = len(words)
        sentences = len([s for s in prompt.split('.') if s.strip()])
        lines = [l.strip() for l in prompt.split('\n') if l.strip()]

        # Calculate scores based on actual content depth, not just keywords
        validation = {}

        # Clarity: Based on length, structure, and organization (more granular)
        clarity = 5.0
        if word_count > 150:
            clarity = 8.5
        elif word_count > 80:
            clarity = 8.0
        elif word_count > 50:
            clarity = 7.5
        elif word_count > 30:
            clarity = 7.0
        elif word_count > 20:
            clarity = 6.5
        elif word_count > 10:
            clarity = 5.5
        # Penalize if has too many sections (sign of generic template)
        section_count = prompt_lower.count('###') + prompt_lower.count('##')
        if section_count > 8:
            clarity = max(2.5, clarity - 1.5)  # Template-like, less clear

        # Specificity: Check for concrete examples and custom details (not generic placeholders)
        specificity = 2.5
        spec_score = 0
        # Actual examples mentioned (not placeholder text)
        actual_examples = prompt.count('[') + prompt.count('{')  # Code/placeholder indicators
        if actual_examples > 0 and "example" in prompt_lower:
            spec_score += 2
        elif "example" in prompt_lower or "such as" in prompt_lower or "for instance" in prompt_lower:
            spec_score += 1.5

        # Concrete details vs generic statements
        if any(x in prompt_lower for x in ["step", "instruction", "procedure", "method"]):
            spec_score += 1.5
        if any(x in prompt_lower for x in ["specific", "concrete", "exact", "particular"]):
            spec_score += 1

        # Penalize if only has generic "example:" text without actual content
        if "example:" in prompt_lower or "[example" in prompt_lower:
            if actual_examples == 0:
                spec_score -= 1  # Generic placeholder, not real example

        if word_count > 80:
            spec_score += 1
        specificity = max(2.5, min(10.0, 3.0 + spec_score))

        # Context: Check for actual audience/purpose definition (not generic)
        context = 2.5
        ctx_score = 0
        # Specific context with details
        context_keywords = sum(1 for x in ["audience:", "target:", "context:", "background:", "purpose:"] if x in prompt_lower)
        if context_keywords > 1:
            ctx_score += 3
        elif any(x in prompt_lower for x in ["audience", "target", "professional", "beginner"]):
            ctx_score += 2
        elif any(x in prompt_lower for x in ["user", "reader"]):
            ctx_score += 1
        if word_count > 50:
            ctx_score += 0.5
        context = max(2.5, min(10.0, 3.0 + ctx_score))

        # Completeness: Check for actual coverage, not just keyword presence
        completeness = 2.5
        comp_score = 0
        # Check for structured sections indicating comprehensive coverage
        has_intro = any(x in prompt_lower for x in ["introduction", "overview", "background"])
        has_details = any(x in prompt_lower for x in ["detail", "specific", "example"])
        has_conclusion = any(x in prompt_lower for x in ["conclusion", "summary", "outcome"])

        sections_count = sum([has_intro, has_details, has_conclusion])
        comp_score += sections_count * 1.5

        if "comprehensive" in prompt_lower or "complete" in prompt_lower:
            comp_score += 1
        if word_count > 100:
            comp_score += 1
        completeness = max(2.5, min(10.0, 3.0 + comp_score))

        # Requirements: Explicit success criteria (not generic placeholder)
        requirements = 2.5
        req_score = 0
        # Real criteria (use "must:", "should:" format) vs generic keywords
        has_must = "must" in prompt_lower and ":" in prompt.lower()
        has_should = "should" in prompt_lower and ":" in prompt.lower()
        if has_must or has_should:
            req_score += 2.5
        elif any(x in prompt_lower for x in ["must", "requirement", "criteria", "success"]):
            req_score += 1.5

        if "expected:" in prompt_lower or "criteria:" in prompt_lower:
            req_score += 1
        if word_count > 40:
            req_score += 0.5
        requirements = max(2.5, min(10.0, 3.0 + req_score))

        # Constraints: Actual boundaries defined (not generic list)
        constraints = 2.5
        con_score = 0
        has_limits = any(x in prompt_lower for x in ["limit:", "constraint:", "boundary:", "maximum:", "minimum:"])
        if has_limits:
            con_score += 2.5
        elif any(x in prompt_lower for x in ["limit", "constraint", "boundary"]):
            con_score += 1.5

        if "avoid" in prompt_lower or "not " in prompt_lower:
            con_score += 1
        constraints = max(2.5, min(10.0, 3.0 + con_score))

        # Expected Output: Specific format not generic template
        expected_output = 2.5
        out_score = 0
        has_format_spec = "format:" in prompt_lower or "output:" in prompt_lower or "structure:" in prompt_lower
        if has_format_spec:
            out_score += 2.5
        elif any(x in prompt_lower for x in ["output", "return", "format", "structure"]):
            out_score += 1.5

        if any(x in prompt_lower for x in ["table", "list", "section", "code", "example"]):
            out_score += 1
        if word_count > 50:
            out_score += 0.5
        expected_output = max(2.5, min(10.0, 3.0 + out_score))

        # Actionability: Real steps not generic placeholder
        actionability = 2.5
        act_score = 0
        # Check for numbered steps or actual procedure
        has_steps = any(f"step {i}:" in prompt_lower for i in range(1, 10)) or "step 1:" in prompt_lower
        if has_steps:
            act_score += 2.5
        elif any(x in prompt_lower for x in ["step", "instruction", "procedure", "guide"]):
            act_score += 1.5

        if any(x in prompt_lower for x in ["action", "implement", "execute", "run"]):
            act_score += 1
        if word_count > 60:
            act_score += 0.5
        actionability = max(2.5, min(10.0, 3.0 + act_score))

        # Build validation dict
        for dim, score in [
            ("clarity", clarity),
            ("specificity", specificity),
            ("context", context),
            ("completeness", completeness),
            ("requirements", requirements),
            ("constraints", constraints),
            ("expected_output", expected_output),
            ("actionability", actionability)
        ]:
            validation[dim] = {
                "level": self._get_level(score),
                "score": min(10.0, max(2.5, score)),
                "issues": [] if score >= 8.0 else ["Could improve"],
                "evidence": f"Analysis of {word_count} words",
                "recommendation": "Good" if score >= 8.0 else "Enhance"
            }

        return {
            "validation": validation,
            "overall_issues": ["Content analysis performed"],
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
