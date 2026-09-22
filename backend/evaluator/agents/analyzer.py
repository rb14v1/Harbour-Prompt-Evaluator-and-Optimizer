import os
import json
from typing import Dict, Any, List
from openai import AzureOpenAI

class AnalyzerAgent:
    """
    Decomposes prompts into key components (intent, requirements, context, constraints, etc.)
    """

    def __init__(self):
        self.name = "Analyzer Agent"
        if os.getenv("DISABLE_AZURE", "false").lower() == "true": self.client = None
        else: self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

    def analyze(self, processed_prompt: str, task_type: str = None) -> Dict[str, Any]:
        """
        Analyze and decompose prompt into key components.

        Args:
            processed_prompt: Normalized prompt text
            task_type: Optional task category for context-aware analysis

        Returns:
            Analysis with intent, requirements, context, constraints, expected output, etc.
        """
        if not self.client:
            return self._extract_intent_from_prompt(processed_prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(task_type)
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this prompt:\n\n{processed_prompt}"
                    }
                ],
                temperature=0.0,
                max_completion_tokens=1500
            )

            response_text = response.choices[0].message.content
            result = self._parse_response(response_text)
            return result

        except Exception as e:
            return self._default_analysis(f"Analysis failed: {str(e)}")

    def _get_system_prompt(self, task_type: str = None) -> str:
        """Return system prompt for analysis."""
        task_context = f"Task type: {task_type}" if task_type else ""

        return f"""You are a rigorous prompt analyzer. Identify gaps, ambiguities, and missing information.

{task_context}

ANALYZE THE PROMPT FOR:
1. Intent: What is the core request?
2. Requirements: What are the EXPLICIT success criteria? (Look for vague words and flag them)
3. Missing Information: What QUESTIONS would a developer ask? (Look for assumptions)
4. Ambiguities: What phrases have MULTIPLE interpretations? (Flag vague terms)
5. Constraints: What are the LIMITS and BOUNDARIES? (Identify missing constraints)
6. Expected Output: What is the EXACT FORMAT required?

Return JSON:
{{
  "intent": "One clear sentence describing the goal",
  "requirements": ["Specific, measurable requirement 1", "Requirement 2"],
  "context": ["Relevant background information"],
  "constraints": ["Specific limit or boundary"],
  "expected_output": "Exact format, example structure",
  "missing_information": ["Critical question that needs answering", "Assumption that needs clarification"],
  "ambiguities": ["Vague term: 'X' could mean A, B, or C", "Unclear phrase and what questions it raises"]
}}

IMPORTANT: Find ACTUAL GAPS, not generic ones. Flag vague words like "quick", "large", "many", "easily", "simple"."""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                # Ensure all fields are present
                return {
                    "intent": str(result.get("intent", "Analysis completed")),
                    "requirements": self._ensure_list(result.get("requirements", [])),
                    "context": self._ensure_list(result.get("context", [])),
                    "constraints": self._ensure_list(result.get("constraints", [])),
                    "expected_output": str(result.get("expected_output", "")),
                    "missing_information": self._ensure_list(result.get("missing_information", [])),
                    "ambiguities": self._ensure_list(result.get("ambiguities", []))
                }
        except (json.JSONDecodeError, ValueError):
            pass

        return self._default_analysis("Could not parse analysis response")

    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _extract_intent_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Extract intent and analysis from prompt text when Azure not available."""
        prompt_lower = prompt.lower()
        words = prompt.split()

        # Extract intent: first sentence or key phrase
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]
        intent = sentences[0] if sentences else prompt[:100]

        # Identify requirements with specifics
        requirements = []
        if "must" in prompt_lower or "should" in prompt_lower:
            requirements.append("Explicit success criteria needed")
        if "step" in prompt_lower or "process" in prompt_lower:
            requirements.append("Sequential process or workflow required")
        if "format" in prompt_lower or "structure" in prompt_lower:
            requirements.append("Specific format or structure expected")
        if not requirements:
            requirements.append("Requirements not explicitly stated")

        # Identify context gaps
        context = []
        if "audience" in prompt_lower or "user" in prompt_lower:
            context.append("Target audience identified")
        elif any(x in prompt_lower for x in ["professional", "technical", "beginner"]):
            context.append("Audience level inferred from terminology")
        else:
            context.append("Target audience not specified")

        if "background" in prompt_lower or "context:" in prompt_lower:
            context.append("Relevant background provided")
        else:
            context.append("Background context missing")

        # Identify constraints/boundaries
        constraints = []
        if "limit" in prompt_lower or "constraint" in prompt_lower:
            constraints.append("Explicit constraints defined")
        if "avoid" in prompt_lower or "not " in prompt_lower or "don't" in prompt_lower:
            constraints.append("Exclusions or boundaries stated")
        if not constraints:
            constraints.append("No explicit boundaries or limitations defined")

        # Expected output
        expected_output = ""
        if "output" in prompt_lower or "format" in prompt_lower:
            expected_output = "Output format specification expected"
        elif "return" in prompt_lower or "provide" in prompt_lower:
            expected_output = "Specific deliverable expected"
        else:
            expected_output = "Output format not clearly specified"

        # Missing information - identify specific gaps
        missing_info = []
        if len(words) < 15:
            missing_info.append("Prompt is too brief; lacks sufficient detail")
        if "example" not in prompt_lower and "such as" not in prompt_lower:
            missing_info.append("No examples provided to clarify expectations")
        if "step" not in prompt_lower and "process" not in prompt_lower and "procedure" not in prompt_lower:
            missing_info.append("Process or workflow not described")
        if "success" not in prompt_lower and "criteria" not in prompt_lower:
            missing_info.append("Success criteria or validation method unclear")
        if "audience" not in prompt_lower and "user" not in prompt_lower:
            missing_info.append("Target audience/stakeholders not identified")
        if not missing_info:
            missing_info.append("Prompt appears reasonably complete")

        # Ambiguities - identify vague or unclear terms
        ambiguities = []
        vague_terms = ["etc", "and so on", "other", "various", "several", "many", "some", "few"]
        for term in vague_terms:
            if term in prompt_lower:
                ambiguities.append(f"'{term}' - vague; specify exact items")

        # Look for undefined terms or concepts
        if any(x in prompt_lower for x in ["it ", "this ", "that ", "the system"]) and len(prompt) > 100:
            if prompt_lower.count("it ") > 2:
                ambiguities.append("Pronoun references unclear; specify what 'it' refers to")

        # Look for vague quality indicators
        vague_quality = ["good", "well", "proper", "appropriate", "reasonable", "suitable"]
        for term in vague_quality:
            if term in prompt_lower:
                ambiguities.append(f"'{term}' - subjective; define specific criteria")

        # Look for unclear scope
        if "include" in prompt_lower and "all" in prompt_lower:
            ambiguities.append("'Include all X' - unclear what constitutes complete coverage")

        if not ambiguities:
            ambiguities.append("No obvious ambiguities detected")

        return {
            "intent": intent,
            "requirements": requirements,
            "context": context,
            "constraints": constraints,
            "expected_output": expected_output,
            "missing_information": missing_info,
            "ambiguities": ambiguities
        }

    def _default_analysis(self, reason: str = "") -> Dict[str, Any]:
        """Return default analysis structure."""
        return {
            "intent": reason or "Analysis incomplete",
            "requirements": [],
            "context": [],
            "constraints": [],
            "expected_output": "",
            "missing_information": ["Full analysis could not be completed"],
            "ambiguities": []
        }
