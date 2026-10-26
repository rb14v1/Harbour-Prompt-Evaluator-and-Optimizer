import logging
from typing import Dict, Any, List
from .llm_client import llm_client

logger = logging.getLogger(__name__)

class Analyzer:
    """
    Analyzes prompt semantics, requirements, constraints, edge cases, and failure modes.
    Uses authoritative frontend department and task_type metadata without any re-classification.
    """

    SYSTEM_PROMPT = """You are an Expert Prompt Analyzer and AI Systems Architect.
Your role is to deeply analyze the user's prompt based on the provided Department and Task Type.
You must NOT re-classify or infer a new department or task type; treat the provided ones as authoritative.

SPEED & CONCISENESS RULE:
Be concise and fast: 1 short sentence for string fields, and 2-3 short items for array fields.

Analyze the prompt thoroughly and return your analysis strictly as a JSON object matching this schema:
{
  "prompt_intent": "Core high-level intention of the prompt (1 sentence)",
  "user_objective": "Primary goal the user wants to accomplish (1 sentence)",
  "explicit_requirements": ["2-3 clearly stated requirements"],
  "implicit_requirements": ["1-2 unstated but logically required details"],
  "context": "Background context or domain setting (1 sentence)",
  "target_audience": "Intended reader or consumer",
  "expected_output": "Description of expected output",
  "output_format": "Expected format (e.g. Markdown, JSON, Code, Table)",
  "constraints": ["2-3 key constraints/rules"],
  "dependencies": ["Required tools or libraries"],
  "missing_information": ["Key missing parameters"],
  "ambiguities": ["Key ambiguities if any"],
  "potential_failure_modes": ["1-2 failure risks"],
  "risks": ["1-2 security or accuracy risks"],
  "edge_cases": ["1-2 tricky inputs or boundary cases"],
  "complexity": "Low | Medium | High",
  "important_assumptions": ["1-2 key assumptions"]
}
"""

    @classmethod
    def analyze(cls, department: str, task_type: str, original_prompt: str, processed_prompt: str) -> Dict[str, Any]:
        prompt_text = processed_prompt or original_prompt

        user_content = f"""Department: {department}
Task Type: {task_type}
Prompt:
\"\"\"
{prompt_text}
\"\"\"
"""
        if llm_client.is_configured():
            res = llm_client.generate_json(cls.SYSTEM_PROMPT, user_content, temperature=0.1)
            if res and isinstance(res, dict) and "prompt_intent" in res:
                res["llm_used"] = True
                return res

        # Intelligent deterministic fallback analysis
        result = cls._fallback_analysis(department, task_type, prompt_text)
        result["llm_used"] = False
        return result

    @classmethod
    def _fallback_analysis(cls, department: str, task_type: str, prompt: str) -> Dict[str, Any]:
        # Determine format hints
        lower = prompt.lower()
        output_format = "Text / Natural Language"
        if "json" in lower:
            output_format = "JSON Object / Schema"
        elif "code" in lower or "function" in lower or "class" in lower or "script" in lower:
            output_format = "Source Code"
        elif "table" in lower or "csv" in lower:
            output_format = "Structured Table"
        elif "email" in lower:
            output_format = "Email Draft"
        elif "markdown" in lower or "documentation" in lower:
            output_format = "Markdown Document"

        # Complexity heuristic
        words = len(prompt.split())
        complexity = "Low" if words < 20 else ("Medium" if words < 80 else "High")

        explicit_reqs = [
            f"Execute {task_type} within {department} scope",
            f"Fulfill main request: '{prompt[:60]}...'" if len(prompt) > 60 else f"Fulfill main request: '{prompt}'"
        ]

        implicit_reqs = [
            "Maintain professional tone and accurate domain terminology",
            "Structure output clearly with readable formatting",
            "Handle common error states or edge conditions appropriately"
        ]

        missing_info = []
        if words < 25:
            missing_info.append("Detailed input parameters, specific styling or formatting schemas")
        if "example" not in lower:
            missing_info.append("Concrete few-shot examples or sample expected outputs")
        if "constraint" not in lower and "limit" not in lower:
            missing_info.append("Explicit length, token, or structural constraints")

        ambiguities = []
        if words < 15:
            ambiguities.append("High-level instruction lacks operational step-by-step guidance")
        if "best" in lower or "good" in lower or "quick" in lower:
            ambiguities.append("Subjective qualifiers like 'best' or 'good' without clear evaluation metrics")

        potential_failure_modes = [
            "LLM producing generic or superficial responses due to lack of constraints",
            "Hallucinating unspecified dependencies or assumptions",
            "Inconsistent response formatting across multiple runs"
        ]

        edge_cases = [
            "Incomplete or malformed user input values",
            "Boundary conditions and unexpected character encodings",
            "Conflicting or contradictory multi-part requirements",
            "Unusually large or minimal input payloads"
        ]

        return {
            "prompt_intent": f"Perform {task_type} for {department}: {prompt[:80]}",
            "user_objective": f"Achieve reliable {task_type} output adhering to {department} standards",
            "explicit_requirements": explicit_reqs,
            "implicit_requirements": implicit_reqs,
            "context": f"{department.capitalize()} department workflow involving {task_type}",
            "target_audience": f"{department.capitalize()} practitioners and stakeholders",
            "expected_output": f"A comprehensive {task_type} deliverable",
            "output_format": output_format,
            "constraints": [
                f"Must conform to {department} domain requirements",
                "Must produce verifiable and logically sound output"
            ],
            "dependencies": ["Standard LLM reasoning capabilities", f"{department} domain standards"],
            "missing_information": missing_info or ["Target length and error recovery details"],
            "ambiguities": ambiguities or ["Under-specified output formatting rules"],
            "potential_failure_modes": potential_failure_modes,
            "risks": ["Inconsistent LLM output format", "Omission of critical edge cases"],
            "edge_cases": edge_cases,
            "complexity": complexity,
            "important_assumptions": [
                "Assumes user provides standard valid inputs",
                f"Assumes standard {department} context and modern best practices"
            ]
        }
