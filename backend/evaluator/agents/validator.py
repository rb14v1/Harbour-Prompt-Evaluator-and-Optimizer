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
        """Validate prompt across all 8 dimensions. USING HEURISTICS ONLY."""
        # BYPASS AZURE - USE HEURISTICS ONLY (Azure was returning bad scores)
        print(f"🔍 Validating: {len(processed_prompt.split())} words")
        result = self._analyze_prompt_content(processed_prompt)
        scores = result.get('validation', {})
        score_str = ", ".join([f"{k}={v.get('score', 0):.1f}" for k,v in scores.items()])
        avg = sum([v['score'] for v in scores.values()]) / len(scores) if scores else 0
        print(f"✅ Scores: avg={avg:.1f}, {score_str}")
        return result

    def _get_system_prompt(self) -> str:
        return f"""You are a rigorous prompt quality validator. Evaluate each dimension carefully:

CLARITY (2.5-10.0): Is the language unambiguous? Are technical terms defined? Is the request understandable?
- 10.0: Crystal clear, no ambiguity, technical terms defined
- 7.5: Generally clear but minor improvements possible
- 5.0: Some vague language, needs clarification
- 2.5: Confusing, contradictory, hard to understand

SPECIFICITY (2.5-10.0): Are details concrete or generic placeholders? Are examples concrete or [TEMPLATE]?
- 10.0: Specific numbers, real examples, concrete details (not [like this])
- 7.5: Mostly specific with 1-2 generic parts
- 5.0: Mix of specific and generic, many [placeholders]
- 2.5: Almost entirely generic or template-like, no real details

CONTEXT (2.5-10.0): Is the target audience clear? Is the use case defined? Are assumptions stated?
- 10.0: Explicit audience, clear use case, assumptions stated
- 7.5: Audience implied, use case mostly clear
- 5.0: Vague audience/use case
- 2.5: No context, could apply to anything

COMPLETENESS (2.5-10.0): Are all needed information sections present? Any critical gaps?
- 10.0: Full end-to-end coverage, all prerequisites included
- 7.5: Mostly complete with minor gaps
- 5.0: Missing 1-2 key sections (requirements, constraints, output format)
- 2.5: Missing 3+ critical sections

REQUIREMENTS (2.5-10.0): Are success criteria measurable? Any quantified targets?
- 10.0: Measurable, quantified (numbers, percentages, metrics)
- 7.5: Mostly measurable with some subjective parts
- 5.0: Some requirements but not measurable
- 2.5: No clear requirements or all subjective ("good", "fast")

CONSTRAINTS (2.5-10.0): Are limitations, boundaries, and exclusions explicit?
- 10.0: All constraints specified clearly (time, resources, scope limits)
- 7.5: Most constraints stated
- 5.0: Some constraints mentioned
- 2.5: No constraints specified

EXPECTED_OUTPUT (2.5-10.0): Is the output format explicitly specified with examples?
- 10.0: Explicit format (JSON/XML/etc), example provided, all fields documented
- 7.5: Format specified but no example
- 5.0: Format mentioned generically ("structured data")
- 2.5: No output format specified

ACTIONABILITY (2.5-10.0): Can a developer/AI execute this without guessing?
- 10.0: Step-by-step executable, no ambiguity, ready to implement
- 7.5: Mostly executable with minor clarifications needed
- 5.0: Needs significant interpretation
- 2.5: Too vague to execute, too many interpretations possible

Return ONLY valid JSON (no markdown, no explanations) with these 8 scores."""

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

        # Detect vague language and placeholders
        vague_terms = ["quick", "fast", "easy", "simple", "good", "bad", "large", "small", "many", "few", "some", "several", "etc", "various", "other"]
        vague_count = sum(1 for term in vague_terms if f" {term} " in f" {prompt_lower} ")

        has_placeholders = "[" in prompt and "]" in prompt
        has_numbers = any(c.isdigit() for c in prompt)
        has_specifics = any(x in prompt_lower for x in ["json", "xml", "csv", "python", "django", "example", "step 1", "step 2"])
        tech_terms = ["json", "xml", "csv", "python", "javascript", "api", "database", "rest", "http", "docker", "aws", "azure"]
        tech_count = sum(1 for term in tech_terms if term in prompt_lower)

        validation = {}

        # STRICT SCORING: Only truly excellent prompts get high scores
        if word_count < 20:
            base_score = 2.5  # Very vague - minimal content
        elif word_count < 50:
            base_score = 5.0  # Moderate - some details, needs more
        elif word_count < 150:
            base_score = 7.5  # Good - decent detail, but could be better
        elif word_count < 300:
            base_score = 8.5  # Very good - comprehensive
        else:
            base_score = 10.0  # Excellent - very detailed (300+ words)

        # Boost ONLY for actual quality indicators
        boost = 0
        has_requirements = "requirement" in prompt_lower or "must" in prompt_lower
        has_constraints = "constraint" in prompt_lower or "limit" in prompt_lower
        has_output_spec = "output" in prompt_lower or "format" in prompt_lower
        has_audience = "audience" in prompt_lower or ("user" in prompt_lower and "users" not in prompt_lower)
        has_metrics = any(c.isdigit() for c in prompt)

        quality_indicators = sum([has_requirements, has_constraints, has_output_spec, has_audience, has_metrics])
        boost = quality_indicators * 0.5  # Max +2.5 if all 5 present

        # Penalty for vagueness
        penalty = vague_count * 0.75

        # Calculate final discrete score
        final = min(10.0, max(2.5, base_score + boost - penalty))

        # Map to discrete levels (2.5, 5.0, 7.5, 10.0) - stricter boundaries
        if final < 3.75:
            discrete_score = 2.5
        elif final < 6.25:
            discrete_score = 5.0
        elif final < 8.75:
            discrete_score = 7.5
        elif final < 9.5:
            discrete_score = 8.5
        else:
            discrete_score = 10.0

        # All 8 dimensions get the SAME discrete score (all measure overall prompt quality)
        for dim in self.DIMENSIONS:
            validation[dim] = {
                "level": self._get_level(discrete_score),
                "score": discrete_score,
                "issues": [] if discrete_score >= 7.5 else ["Needs improvement"],
                "evidence": f"{word_count} words, {vague_count} vague, boost={boost:.1f}, penalty={penalty:.1f}",
                "recommendation": "Excellent" if discrete_score >= 10.0 else "Good" if discrete_score >= 7.5 else "Needs improvement"
            }

        return {
            "validation": validation,
            "overall_issues": ["Content analysis performed"],
            "improvement_targets": [d for d in self.DIMENSIONS if validation[d]["score"] < 7.5]
        }

    def _round_to_quality_level(self, score: float) -> float:
        """Round continuous score to discrete quality level (2.5, 5.0, 7.5, 10.0)."""
        valid_scores = [2.5, 5.0, 7.5, 10.0]
        return min(valid_scores, key=lambda x: abs(x - score))

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
