import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from .llm_client import llm_client

logger = logging.getLogger(__name__)

DIFFICULTIES = ["Easy", "Medium", "Hard"]


class LLMCaseGrader:
    """
    Grades each synthetic test case with an LLM judge: does the improved prompt
    satisfy the case's expected output? One LLM call grades one whole dataset.
    """

    PASS_THRESHOLD = 7.0

    SYSTEM_PROMPT = """You are a strict test case grader for prompt engineering.
For each test case, judge whether the improved prompt would make a model produce output that
satisfies the case's expected output. Score 0 to 10: 10 means fully satisfied, 0 means not addressed.
Return strict JSON:
{"grades": [{"test_case_id": "TC-001", "score": 7, "reason": "one short sentence"}]}
Grade every test case you receive. Do not skip any."""

    @classmethod
    def _ungraded(cls) -> Dict[str, Any]:
        return {"llm_score": None, "llm_verdict": "UNGRADED", "llm_reason": ""}

    @classmethod
    def grade_dataset(cls, improved_prompt: str, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not test_cases:
            return []
        if not llm_client.is_configured():
            return [cls._ungraded() for _ in test_cases]

        cases_payload = [
            {
                "test_case_id": tc.get("test_case_id", ""),
                "difficulty": tc.get("difficulty", ""),
                "input": tc.get("input", ""),
                "expected_output": tc.get("expected_output", "")
            }
            for tc in test_cases
        ]
        user_content = (
            "Improved prompt:\n"
            + improved_prompt + "\n\n"
            + "Test cases:\n"
            + json.dumps(cases_payload, ensure_ascii=False)
        )
        res = llm_client.generate_json(cls.SYSTEM_PROMPT, user_content, temperature=0.0)
        grades = {}
        if res and isinstance(res, dict):
            for g in res.get("grades", []):
                if isinstance(g, dict) and "test_case_id" in g:
                    grades[str(g["test_case_id"])] = g

        out = []
        for tc in test_cases:
            g = grades.get(str(tc.get("test_case_id", "")))
            if g is None or not isinstance(g.get("score"), (int, float)):
                out.append(cls._ungraded())
                continue
            score = float(g["score"])
            out.append({
                "llm_score": score,
                "llm_verdict": "PASS" if score >= cls.PASS_THRESHOLD else "FAIL",
                "llm_reason": str(g.get("reason", ""))[:300]
            })
        return out

    @classmethod
    def grade_datasets(cls, improved_prompt: str, datasets: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        with ThreadPoolExecutor(max_workers=50) as executor:
            return list(executor.map(
                lambda item: cls.grade_dataset(improved_prompt, item["dataset"].get("test_cases", [])),
                datasets
            ))

    @classmethod
    def summarise(cls, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        def block(subset: List[Dict[str, Any]]) -> Dict[str, Any]:
            graded = [c for c in subset if c.get("llm_verdict") in ("PASS", "FAIL")]
            passing = sum(1 for c in graded if c["llm_verdict"] == "PASS")
            scores = [c["llm_score"] for c in graded if c.get("llm_score") is not None]
            return {
                "cases": len(subset),
                "graded": len(graded),
                "passing": passing,
                "pass_rate": round(passing / len(graded) * 100, 1) if graded else 0.0,
                "avg_score": round(sum(scores) / len(scores), 2) if scores else None
            }

        overall = block(cases)
        return {
            "total_test_cases": overall["cases"],
            "graded_cases": overall["graded"],
            "passing_cases": overall["passing"],
            "failing_cases": overall["graded"] - overall["passing"],
            "pass_rate": overall["pass_rate"],
            "avg_score": overall["avg_score"],
            "coverage_by_difficulty": {
                d: block([c for c in cases if c.get("difficulty") == d]) for d in DIFFICULTIES
            },
            "strengths": [],
            "remaining_gaps": []
        }
