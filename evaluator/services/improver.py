import logging
import json
from typing import Dict, Any
from .llm_client import llm_client

logger = logging.getLogger(__name__)

class Improver:
    """
    Prompt Improver Agent.
    Transforms the original prompt into an optimized, robust, structured prompt
    addressing all 15-dimension evaluation weaknesses while strictly preserving user intent.
    """

    SYSTEM_PROMPT = """You are a World-Class AI Prompt Optimization Engineer.

MISSION: Rewrite the user's prompt into a prompt that a target LLM can follow reliably, so the target LLM's output passes the synthetic test cases and scores higher on the 15 quality dimensions.

Write the improved prompt as direct instructions to the target LLM. Never copy the user's prompt or any of its sentences, never quote it, never describe it ("the original prompt says..."), and never write a report about it.

SIZING RULE (length depends on the input length given in the request). Every size uses tags.
- Short input (under 100 words): write a longer improved prompt with at least <role>, <context>, <constraints> and <output_format>. Explain each tag's content fully, drawing only on the user's prompt.
- Medium input (100 to 300 words): write a balanced improved prompt with at least <role>, <context>, <constraints> and <output_format>, each explained briefly.
- Long input (over 300 words): write a compact improved prompt. Use only the five tags <role>, <context>, <constraints>, <output_format> and <examples>, and keep each tag to its essentials.

CONTENT RULES:
1. Keep the user's intent, facts and required outputs. Draw every fact from the user's prompt, but write each line as your own instruction to the target LLM. Do not paste the user's sentences, bullets or tables into the tags. Do not add generic advice, invented facts, audiences, versions, limits, policies or roles the user did not give.
2. If a detail the target LLM needs is missing, add a [SPECIFY X] placeholder. Add a placeholder only where it is needed.
3. Turn the user's material into instructions: state the task, the steps in order, and the exact output format.
4. Address each weakness (score < 6) only where it applies: clarity with <context>, context_completeness and constraints with <constraints>, output_format with <examples>, robustness with an edge-case or error-handling instruction.
5. Every opening tag must have a matching closing tag. Tags must not nest.
6. Use <examples> only when the user supplied examples or the output_format weakness exists. Include at most one example inside <examples>.
7. Use only the five tags for long input. For short input, any tag the task needs is allowed.

Return your response as a strict JSON object:
{
  "improved_prompt": "The complete improved prompt text, written as instructions to the target LLM",
  "explanation_of_changes": [
    "Added <constraints> listing excluded inputs",
    "Clarified <output_format> with an explicit schema"
  ],
  "structural_sections_added": [
    "role", "context", "constraints", "output_format"
  ]
}

WEAKNESS-TO-ACTION MAPPING:
- clarity < 6 → Add <context> with explicit definitions
- context_completeness < 6 → Add <context> with background from the user's prompt only; use [SPECIFY X] for gaps
- constraints < 6 → Add <constraints> listing what's excluded
- robustness < 6 → Add an edge-case or error-handling instruction, only for situations the user's prompt covers
- output_format < 6 → Add one concrete example inside <examples> and an explicit <output_format> schema
"""

    STRIP_PROMPT = """You audit a rewritten prompt against the original prompt.
Keep every technology, tool, audience, format and constraint that appears in the original prompt,
using the same names. Remove only facts that appear in the rewritten prompt but not in the original:
invented technologies, audiences, versions, environments, databases, team roles or word limits.
Keep the structure and every instruction grounded in the original prompt. Keep the XML tag structure.
Where a required detail is missing from both prompts, replace it with a [SPECIFY ...] placeholder.
Do not replace a term that the original prompt already states.
Return strict JSON: {"improved_prompt": "the cleaned prompt text"}"""

    @classmethod
    def _strip_assumptions(cls, original_prompt: str, improved_prompt: str) -> str:
        if not llm_client.is_configured():
            return improved_prompt
        user_content = f"""Original prompt:
\"\"\"
{original_prompt}
\"\"\"

Rewritten prompt:
\"\"\"
{improved_prompt}
\"\"\"
"""
        res = llm_client.generate_json(cls.STRIP_PROMPT, user_content, temperature=0.0)
        if res and isinstance(res, dict) and res.get("improved_prompt"):
            return str(res["improved_prompt"]).strip()
        return improved_prompt

    @classmethod
    def improve(
        cls,
        department: str,
        task_type: str,
        original_prompt: str,
        processed_prompt: str,
        analysis: Dict[str, Any],
        evaluation: Dict[str, Any],
        dataset_evidence: str = ""
    ) -> Dict[str, Any]:

        dims = evaluation.get("dimensions", {})
        weaknesses = []
        for k, v in dims.items():
            if isinstance(v, dict) and v.get("score", 10) < 6:
                weaknesses.append(f"- {v.get('name', k)} (Score: {v.get('score')}): {v.get('identified_issue', '')} -> Recommendation: {v.get('recommendation', '')}")

        source_prompt = processed_prompt or original_prompt
        original_words = len(source_prompt.split())
        user_content = f"""Department: {department}
Task Type: {task_type}

Original Prompt ({original_words} words):
\"\"\"
{source_prompt}
\"\"\"

Original prompt length: {original_words} words. Size the improved prompt by the sizing rule.

Key Weaknesses to Fix:
{chr(10).join(weaknesses[:3]) if weaknesses else "- Add role, constraints, and output format."}

Intent: {analysis.get('prompt_intent', '')}
Output Format: {analysis.get('output_format', '')}
{f"""
Test Suite Evidence (generated test datasets run against the original prompt):
{dataset_evidence}
""" if dataset_evidence else ''}
Please produce the optimized prompt in strict JSON format.
"""
        if llm_client.is_configured():
            res = llm_client.generate_json(cls.SYSTEM_PROMPT, user_content, temperature=0.2)
            if res and isinstance(res, dict) and "improved_prompt" in res:
                cleaned = cls._strip_assumptions(
                    processed_prompt or original_prompt,
                    res["improved_prompt"].strip()
                )
                return {
                    "improved_prompt": cleaned,
                    "explanation_of_changes": res.get("explanation_of_changes", [
                        "Added modular role and context structure",
                        "Defined explicit output schema and guardrails",
                        "Included negative constraints to prevent hallucinations"
                    ]),
                    "structural_sections_added": res.get("structural_sections_added", [
                        "Role & Context", "Step-by-Step Instructions", "Output Schema", "Constraints"
                    ]),
                    "llm_used": True
                }

        # Fallback intelligent prompt optimization
        result = cls._fallback_improve(department, task_type, processed_prompt or original_prompt, analysis, evaluation)
        result["llm_used"] = False
        return result

    @classmethod
    def _fallback_improve(
        cls,
        department: str,
        task_type: str,
        prompt: str,
        analysis: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        output_format = analysis.get("output_format", "Structured Markdown")
        intent = analysis.get("prompt_intent", prompt)
        user_obj = analysis.get("user_objective", f"Complete {task_type} for {department}")

        improved_text = f"""<role>
You are an expert {department.capitalize()} specialist. Your goal is to: {user_obj}.
</role>

<context>
{prompt}
</context>

<output_format>
Deliver the output formatted as {output_format}.
</output_format>

<constraints>
- Do NOT fabricate non-existent packages, APIs, or unverified facts.
</constraints>
"""
        return {
            "improved_prompt": improved_text.strip(),
            "explanation_of_changes": [
                "Wrapped the prompt in XML tags (role, context, output_format, constraints).",
                "Added an explicit output format and guardrails against hallucinations."
            ],
            "structural_sections_added": [
                "role",
                "instructions",
                "output_format",
                "constraints"
            ]
        }
