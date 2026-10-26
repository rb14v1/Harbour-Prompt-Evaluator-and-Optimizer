import logging
from typing import Dict, Any, Optional
from .evaluator import Evaluator, EVALUATION_DIMENSIONS
from .llm_client import llm_client
import json

logger = logging.getLogger(__name__)

class Revalidator:
    """
    Independent Re-Validator.
    Re-evaluates the improved prompt across 15 quality dimensions using blind evaluation
    (LLM does not know the original scores). Fallback uses heuristic analysis.
    """

    SYSTEM_PROMPT = """You are an independent Prompt Quality Re-Validator conducting a blind evaluation.

CRITICAL: You are NOT aware of the original prompt's scores. Evaluate THIS prompt on its own merits (0-10).

Evaluate across these 15 dimensions, using these exact keys:
1. instruction_following - Are instructions clear and direct?
2. clarity - Is the prompt readable, structured and in plain language?
3. specificity - Are granular details, parameters and edge case definitions given?
4. context_completeness - Is there sufficient background, persona and domain information?
5. output_format - Is the expected output format clearly specified?
6. constraints - Are negative constraints, length limits and rules defined?
7. robustness - Is it resilient to ambiguous or invalid inputs?
8. ambiguity - Score 10 = completely unambiguous, 0 = highly ambiguous
9. safety - Does it mitigate hallucinations and insecure behaviour?
10. reusability - Can it be adapted for other contexts?
11. maintainability - Is it easy to update and extend?
12. llm_friendliness - Is it easy for an LLM to follow?
13. token_efficiency - Is it free of unnecessary length?
14. scalability - Does it account for scale and growth?
15. overall_prompt_design - Is the overall design coherent and effective?

RETURN ONLY VALID JSON (no markdown, no explanation):
{
  "dimensions": {
    "instruction_following": {"score": 8, "reasoning": "..."},
    "context_completeness": {"score": 7, "reasoning": "..."},
    ...all 15 dimensions...
  },
  "overall_score": 7.5,
  "summary": "Independent re-evaluation findings"
}

Each score: 0-10 scale. Be critical and objective. Rate based on the prompt's absolute quality, not improvement."""

    @classmethod
    def reevaluate(
        cls,
        department: str,
        task_type: str,
        improved_prompt: str,
        original_evaluation: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Independent re-evaluation of improved prompt.
        Uses LLM if configured (blind evaluation), falls back to heuristic if not.
        """
        logger.info("Re-validating improved prompt (blind evaluation)")

        # Try LLM first
        if llm_client.is_configured():
            user_content = f"""PROMPT TO EVALUATE:
{improved_prompt}

Department: {department}
Task Type: {task_type}"""

            res = llm_client.generate_json(cls.SYSTEM_PROMPT, user_content, temperature=0.1)
            if res and "dimensions" in res:
                logger.info("LLM re-validation completed")
                res["llm_used"] = True
                return res

        # Fallback: use heuristic evaluation
        logger.warning("LLM re-validation failed or not configured, using heuristic")
        return cls._fallback_reevaluate(department, task_type, improved_prompt, analysis)

    @classmethod
    def _fallback_reevaluate(
        cls,
        department: str,
        task_type: str,
        improved_prompt: str,
        analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Heuristic-based re-evaluation when LLM unavailable.
        Uses structural analysis of the improved prompt.
        """
        # Reuse evaluator's fallback logic on the improved prompt
        dims = Evaluator._fallback_evaluate(department, task_type, improved_prompt, analysis or {})

        return {
            "dimensions": dims.get("dimensions", {}),
            "overall_score": dims.get("overall_score", 5.0),
            "summary": "Heuristic re-evaluation (LLM unavailable)",
            "llm_used": False
        }
