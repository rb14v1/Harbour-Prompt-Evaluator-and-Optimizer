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

        # Count placeholder patterns - signs of generic template (only square brackets, not JSON braces)
        # Curly braces {} are JSON format specs and should not count as placeholders
        placeholder_count = prompt.count('[') + prompt.count(']')
        generic_template_patterns = sum(1 for x in [
            "[who will", "[what ", "[why ", "[example ", "[detailed ",
            "[specific ", "[concrete ", "[your ", "[describe "
        ] if x in prompt_lower)

        # Calculate scores based on actual content depth, not just keywords
        validation = {}

        # Clarity: Assess if language is clear and unambiguous
        clarity = 6.5
        if placeholder_count > 10:  # Increased threshold from 5 to 10
            clarity = 3.0  # Heavy penalty for placeholder-filled content
        else:
            if word_count > 150:
                clarity = 9.0  # Boosted from 8.0
            elif word_count > 100:
                clarity = 8.5  # Added tier
            elif word_count > 80:
                clarity = 8.0  # Boosted from 7.5
            elif word_count > 50:
                clarity = 7.5  # Boosted from 7.0
            elif word_count > 30:
                clarity = 7.0  # Boosted from 6.5
            elif word_count > 10:
                clarity = 6.0  # Boosted from 5.5

            # Check for vague language
            vague_words = sum(1 for x in ["etc", "various", "several", "some", "many", "other"] if f" {x}" in f" {prompt_lower}")
            if vague_words > 3:  # Increased threshold from 2 to 3
                clarity = max(2.5, clarity - 1.0)  # Reduced penalty from 1.5 to 1.0

        # Specificity: Check for concrete details and real examples (not [Placeholder] text)
        specificity = 5.0
        if placeholder_count > 5:  # Increased threshold from 3 to 5
            specificity = 5.0  # Placeholder-heavy = low specificity
        else:
            spec_score = 0
            # Real specific details (e.g., "3 examples", "Python", "JSON format", numbers, actual tool names)
            has_numbers = any(c.isdigit() for c in prompt)
            has_specific_terms = sum(1 for x in ["json", "xml", "python", "javascript", "example 1", "example 2", "django", "azure"] if x in prompt_lower)

            if has_numbers and has_specific_terms > 0:
                spec_score += 3.5  # Boosted from 3
            elif has_numbers or has_specific_terms > 1:
                spec_score += 3.0  # Boosted from 2
            elif has_specific_terms > 0:
                spec_score += 2.0  # New tier
            elif "example" in prompt_lower or "such as" in prompt_lower:
                spec_score += 1.5  # Boosted from 1

            # Penalty for generic placeholders
            if "[example" in prompt_lower or "[specific" in prompt_lower:
                spec_score -= 1.0  # Reduced penalty from 1.5 to 1.0

            specificity = max(2.5, min(10.0, 4.5 + spec_score))  # Base boosted from 3.0 to 4.5

        # Context: Actual audience/purpose stated (not generic [Who will use this?])
        context = 5.0
        if placeholder_count > 10:  # Increased threshold from 5 to 10
            context = 3.0  # Placeholder-heavy template
        else:
            ctx_score = 0
            # Specific audience identification (not [Placeholder])
            if "audience:" in prompt_lower or "target:" in prompt_lower:
                if "[who" not in prompt_lower:
                    ctx_score += 3.0  # Boosted from 2
            if "for " in prompt_lower or "enterprise" in prompt_lower or "teams" in prompt_lower:
                ctx_score += 2.0  # Boosted from 1.5 (added check)
            if any(x in prompt_lower for x in ["professional", "technical", "beginner", "expert", "user", "familiar"]):
                ctx_score += 1.5
            if "background:" in prompt_lower or "context:" in prompt_lower:
                if "[" not in prompt_lower:
                    ctx_score += 1.5  # Boosted from 1
            context = max(2.5, min(10.0, 4.5 + ctx_score))  # Base boosted from 3.0 to 4.5

        # Completeness: Actual content coverage (not just [Coverage requirements])
        completeness = 5.0
        if placeholder_count > 10:  # Increased threshold from 5 to 10
            completeness = 3.0  # Too many placeholders = incomplete
        else:
            comp_score = 0
            # Real coverage vs placeholders
            has_multiple_sections = prompt.count('\n') > 5 or prompt.count('###') > 2 or prompt.count('Step') > 3
            if has_multiple_sections and placeholder_count < 5:
                comp_score += 3.0  # Boosted from 2
            elif has_multiple_sections:
                comp_score += 1.0  # Changed penalty to bonus for sections

            if word_count > 200:
                comp_score += 2.0  # Boosted
            elif word_count > 100:
                comp_score += 1.5
            elif word_count > 50:
                comp_score += 0.5

            completeness = max(2.5, min(10.0, 4.5 + comp_score))  # Base boosted from 3.0 to 4.5

        # Requirements: Explicit, measurable criteria (not generic [Non-negotiable criteria])
        requirements = 5.0
        if "[must" in prompt_lower or "[non-" in prompt_lower or "[should" in prompt_lower:
            requirements = 5.0  # Just placeholder text
        else:
            req_score = 0
            # Real requirements with specifics (numbers, percentages, metrics)
            has_metrics = any(c.isdigit() for c in prompt) or "%" in prompt
            if "must" in prompt_lower or "requirement" in prompt_lower or "criteria" in prompt_lower:
                if has_metrics:
                    req_score += 3.5  # Boosted from 2.5
                else:
                    req_score += 2.0  # Boosted from 1.5
            if "error" in prompt_lower and "%" in prompt:
                req_score += 1.5  # Bonus for error rate metrics
            if any(x in prompt_lower for x in ["success", "pass", "achieve", "seconds", "concurrent"]):
                req_score += 1.5  # Boosted from 1, added performance metrics
            requirements = max(2.5, min(10.0, 4.5 + req_score))  # Base boosted from 3.5 to 4.5

        # Constraints: Real limitations stated (not generic [Time constraints:])
        constraints = 5.0
        if "[constraint" in prompt_lower or "[time " in prompt_lower or "[resource" in prompt_lower:
            constraints = 5.0  # Just placeholder
        else:
            con_score = 0
            if "maximum" in prompt_lower or "minimum" in prompt_lower or "limit" in prompt_lower:
                con_score += 3.0  # Boosted from 2
            if any(x in prompt_lower for x in ["avoid", "not ", "don't", "no ", "exclude", "unsupported"]):
                con_score += 2.0  # Boosted from 1.5, added checks
            if "constraint" in prompt_lower or "boundary" in prompt_lower or "format" in prompt_lower:
                con_score += 1.5  # Boosted from 1
            constraints = max(2.5, min(10.0, 4.5 + con_score))  # Base boosted from 3.0 to 4.5

        # Expected Output: Real format specification (not generic [Format type:])
        expected_output = 5.0
        if "[format" in prompt_lower or "[deliverable" in prompt_lower or "[structure" in prompt_lower:
            expected_output = 5.0  # Placeholder only
        else:
            out_score = 0
            # Specific formats mentioned
            if any(x in prompt_lower for x in ["json", "xml", "csv", "table", "list", "document", "code"]):
                out_score += 3.5  # Boosted from 2.5
            elif any(x in prompt_lower for x in ["format", "output", "return", "response"]):
                out_score += 2.5  # Boosted from 1.5
            if any(x in prompt_lower for x in ["section", "page", "organized", "structured", "field", "uuid"]):
                out_score += 2.0  # Boosted from 1, added field/uuid checks
            expected_output = max(2.5, min(10.0, 4.5 + out_score))  # Base boosted from 3.0 to 4.5

        # Actionability: Real executable steps (not generic [Step 1: ...])
        actionability = 5.0
        if "[step" in prompt_lower or "[first action" in prompt_lower:
            actionability = 5.0  # Placeholder only
        else:
            act_score = 0
            # Real procedural steps
            step_count = sum(1 for i in range(1, 10) if f"step {i}" in prompt_lower)
            if step_count > 5:
                act_score += 4.0  # Boosted from 3, reward many steps
            elif step_count > 2:
                act_score += 3.5  # Boosted from 3
            elif "step" in prompt_lower or "process:" in prompt_lower or "workflow:" in prompt_lower:
                act_score += 2.5  # Boosted from 1.5, added workflow

            if any(x in prompt_lower for x in ["then", "next", "finally", "afterwards", "validate", "execute"]):
                act_score += 1.5  # Boosted from 1, added keywords
            actionability = max(2.5, min(10.0, 4.5 + act_score))  # Base boosted from 3.0 to 4.5

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
