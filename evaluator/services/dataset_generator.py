import logging
import json
from typing import Dict, Any, List, Optional
from .llm_client import llm_client

logger = logging.getLogger(__name__)

class DatasetGenerator:
    """
    Synthetic Dataset Generation Agent.
    Generates a prompt-specific test dataset across Easy, Medium, and Hard scenarios with dynamic categories.
    """

    SYSTEM_PROMPT = """You are a Synthetic Dataset Generation Agent.

MISSION: Generate test cases that identify if an improved prompt actually addresses weaknesses.

CRITICAL CONTEXT:
- You are given evaluation scores (15 dimensions) showing the original prompt's weaknesses
- Low-scoring dimensions (< 5.0) MUST get hard/edge case tests
- These test cases will be used to validate an improved prompt later
- Success = Improved prompt passes more test cases than original

You are given:
- Department & Task Type
- Original Prompt (the prompt being evaluated)
- Prompt Intent, Requirements, Constraints
- EVALUATION SCORES (15 dimensions) ← These show what to test
- Target Dataset Size (e.g., 5: 2 Easy, 2 Medium, 1 Hard)

Your Job:
1. Generate test cases that target the WEAKNESSES (low dimension scores)
2. Make tests hard enough to reveal if improvement worked
3. Ensure tests are verifiable (expected output must be concrete)

Each test case must contain:
- prompt_id (e.g. "PROMPT-001")
- test_case_id (e.g. "TC-001", "TC-002", ...)
- input (realistic scenario that tests a specific requirement)
- expected_output (concrete output that demonstrates requirement met)
- difficulty ("Easy" | "Medium" | "Hard")
- category (domain-specific, e.g., "Error Handling", "Edge Cases")
- notes (validation criteria - how to verify if output is correct)
- edge_case (boolean: true if boundary/exceptional condition)

TARGETING STRATEGY - Generate tests based on evaluation scores:

IF clarity < 5.0:
  → Test with ambiguous or complex inputs
  → Expected output should show clear structure

IF robustness < 5.0:
  → HARD cases: Missing parameters, boundary conditions, conflicting instructions, invalid inputs, null values
  → Expected output should show graceful handling and error handling

IF context_completeness < 5.0:
  → Test with multi-part requirements
  → Expected output should address all parts

DIFFICULTY DISTRIBUTION (by evaluation scores):
- Easy (40%): Tests basic requirements that scored well (> 7.0)
- Medium (40%): Tests requirements with moderate scores (5-7)
- Hard (20%): Tests weak areas scoring < 5.0 OR edge cases

Requirements:
1. Every test case must target a specific requirement or weakness.
2. Do NOT generate generic unrelated test cases.
3. Hard cases MUST test low-scoring dimensions (< 5.0).
4. Expected output must be CONCRETE and VERIFIABLE (not vague).
5. Keep inputs & outputs concise but complete (1-3 sentences).
6. Categories must match the prompt's domain.
7. Return strictly valid JSON with key "test_cases": [ ... ].
"""

    @classmethod
    def generate(
        cls,
        department: str,
        task_type: str,
        original_prompt: str,
        processed_prompt: str,
        analysis: Dict[str, Any],
        dataset_size: int = 5,
        prompt_id: str = "PROMPT-001",
        variation_index: int = 1,
        variation_total: int = 1
    ) -> Dict[str, Any]:

        variation_line = (
            f"Variation: {variation_index} of {variation_total}. Choose scenarios, inputs and categories "
            f"that differ from a typical first draft so this dataset is distinct from the other variations.\n"
            if variation_total > 1 else ""
        )

        # Calculate target distribution
        if dataset_size == 5:
            easy_count = 2
            medium_count = 2
            hard_count = 1
        elif dataset_size == 6:
            easy_count = 2
            medium_count = 2
            hard_count = 2
        else:
            easy_count = max(1, int(round(dataset_size * 0.35)))
            hard_count = max(1, int(round(dataset_size * 0.25)))
            medium_count = max(1, dataset_size - easy_count - hard_count)

        user_content = f"""Department: {department}
Task Type: {task_type}
Prompt ID: {prompt_id}
Target Dataset Size: {dataset_size} (2 Easy, 2 Medium, 1 Hard)
{variation_line}
Prompt Text:
\"\"\"
{processed_prompt or original_prompt}
\"\"\"

Intent: {analysis.get('prompt_intent', '')}
Output Format: {analysis.get('output_format', '')}
Constraints: {', '.join(analysis.get('constraints', [])[:3])}

Please generate exactly {dataset_size} prompt-specific test cases (2 Easy, 2 Medium, 1 Hard) as JSON:
{{
  "test_cases": [
    {{
      "prompt_id": "{prompt_id}",
      "test_case_id": "TC-001",
      "input": "...",
      "expected_output": "...",
      "difficulty": "Easy",
      "category": "...",
      "notes": "...",
      "edge_case": false
    }}
  ]
}}
"""
        if llm_client.is_configured():
            res = llm_client.generate_json(cls.SYSTEM_PROMPT, user_content, temperature=0.3)
            if res and isinstance(res, dict) and "test_cases" in res and isinstance(res["test_cases"], list):
                raw_cases = res["test_cases"]
                if len(raw_cases) >= int(dataset_size * 0.7):
                    # Format IDs properly
                    formatted = []
                    for idx, tc in enumerate(raw_cases, start=1):
                        tc_id = tc.get("test_case_id") or f"TC-{idx:03d}"
                        formatted.append({
                            "prompt_id": prompt_id,
                            "test_case_id": tc_id,
                            "input": str(tc.get("input", "")).strip(),
                            "expected_output": str(tc.get("expected_output", "")).strip(),
                            "difficulty": tc.get("difficulty", "Medium").capitalize() if str(tc.get("difficulty", "")).capitalize() in ["Easy", "Medium", "Hard"] else "Medium",
                            "category": str(tc.get("category", "General")).strip(),
                            "notes": str(tc.get("notes", "Generated test case.")).strip(),
                            "edge_case": bool(tc.get("edge_case", False) or tc.get("difficulty") == "Hard")
                        })

                    # Validate difficulty distribution
                    diff_dist = cls._validate_difficulty_distribution(formatted, easy_count, medium_count, hard_count)
                    if diff_dist.get("is_valid"):
                        return {
                            "dataset_size": len(formatted),
                            "test_cases": formatted,
                            "llm_used": True
                        }
                    else:
                        logger.warning(f"LLM difficulty distribution skewed: {diff_dist.get('actual', {})}. Using fallback generation.")
                        # Fall through to fallback if distribution is bad

        # Fallback intelligent prompt-specific synthetic dataset generation
        result = cls._fallback_generate(department, task_type, processed_prompt or original_prompt, analysis, dataset_size, prompt_id)
        result["llm_used"] = False
        return result

    @classmethod
    def _fallback_generate(
        cls,
        department: str,
        task_type: str,
        prompt: str,
        analysis: Dict[str, Any],
        dataset_size: int = 5,
        prompt_id: str = "PROMPT-001"
    ) -> Dict[str, Any]:
        """
        Creates rich, domain-tailored test cases matching the specific prompt when LLM API is unavailable.
        """
        if dataset_size == 5:
            easy_count = 2
            medium_count = 2
            hard_count = 1
        elif dataset_size == 6:
            easy_count = 2
            medium_count = 2
            hard_count = 2
        else:
            easy_count = max(1, int(round(dataset_size * 0.35)))
            hard_count = max(1, int(round(dataset_size * 0.25)))
            medium_count = max(1, dataset_size - easy_count - hard_count)

        categories = cls._derive_dynamic_categories(department, task_type, prompt)
        output_format = analysis.get("output_format", "Structured Output")

        test_cases = []
        tc_counter = 1

        # 1. Generate Easy cases
        for i in range(easy_count):
            cat = categories[i % len(categories)]
            tc = {
                "prompt_id": prompt_id,
                "test_case_id": f"TC-{tc_counter:03d}",
                "input": f"Standard {department} scenario for {task_type}: Execute '{prompt[:50]}' with clean baseline parameters (Sample Case #{i+1}).",
                "expected_output": f"Clear, properly formatted {output_format} containing verified baseline {task_type} results adhering to {department} specifications.",
                "difficulty": "Easy",
                "category": cat,
                "notes": f"Baseline validation of primary intent under ideal input conditions ({cat}).",
                "edge_case": False
            }
            test_cases.append(tc)
            tc_counter += 1

        # 2. Generate Medium cases
        medium_variations = [
            ("Multi-attribute requirement with secondary constraints", "Must include contextual metadata, error notes, and structured sections"),
            ("Composite input payload containing nested parameters", "Verify all nested fields are extracted and rendered correctly"),
            ("Domain-specific terminology and compliance terms", "Ensure accurate usage of professional jargon without hallucination"),
            ("Real-world scenario with mixed data types", "Parse dates, numbers, strings, and boolean flags consistently"),
            ("Output size constraint validation", "Ensure response stays within target boundary without truncating essential context"),
            ("Comparative request across multiple entities", "Provide side-by-side structured comparison following format rules"),
            ("Ambiguous input requiring safe conservative defaults", "Apply standard fallback conventions and state assumptions"),
            ("Informal input requiring professional normalization", "Convert informal phrasing to formal department deliverable"),
            ("Multi-step operational sequence execution", "Follow step 1 to N rigorously in designated execution order")
        ]

        for i in range(medium_count):
            variation_title, variation_detail = medium_variations[i % len(medium_variations)]
            cat = categories[(i + easy_count) % len(categories)]
            tc = {
                "prompt_id": prompt_id,
                "test_case_id": f"TC-{tc_counter:03d}",
                "input": f"{variation_title}: Input for '{prompt[:45]}...' with {variation_detail}.",
                "expected_output": f"Comprehensive {output_format} that correctly addresses all secondary constraints and renders complete output for {department}.",
                "difficulty": "Medium",
                "category": cat,
                "notes": f"Validates multi-constraint handling and schema precision ({cat}).",
                "edge_case": False
            }
            test_cases.append(tc)
            tc_counter += 1

        # 3. Generate Hard / Edge cases
        hard_variations = [
            ("Missing required parameters / partial input", "Prompt should gracefully report missing fields or use documented defaults rather than crashing or hallucinating", True, "Incomplete Input"),
            ("Conflicting instructions or contradictory constraints", "Prompt should prioritize safety/core requirements and explicitly flag contradiction", True, "Conflicting Directives"),
            ("Boundary conditions with extreme payload length or zero records", "Output must handle empty sets or maximum payload thresholds cleanly", True, "Boundary Condition"),
            ("Malformed text containing special characters and code delimiters", "Prompt must preserve literal strings without parsing errors or injection vulnerability", True, "Malformed Encoding"),
            ("Adversarial or out-of-domain edge case", "Prompt should safely constrain output to designated department scope without wandering", True, "Domain Boundary Case"),
            ("Nested hierarchical data with null values", "Prompt should process valid branches and null-coalesce missing leaf nodes", True, "Null / Missing Fields")
        ]

        for i in range(hard_count):
            var_title, expected_beh, is_edge, edge_cat = hard_variations[i % len(hard_variations)]
            cat = edge_cat if edge_cat in categories else categories[i % len(categories)]
            tc = {
                "prompt_id": prompt_id,
                "test_case_id": f"TC-{tc_counter:03d}",
                "input": f"[EDGE CASE] {var_title} applied to prompt task '{prompt[:40]}...'.",
                "expected_output": f"Robust response: {expected_beh}. Must maintain {output_format} integrity without uncaught errors.",
                "difficulty": "Hard",
                "category": cat,
                "notes": f"Edge case resilience test for {var_title.lower()}.",
                "edge_case": True
            }
            test_cases.append(tc)
            tc_counter += 1

        return {
            "dataset_size": len(test_cases),
            "test_cases": test_cases
        }

    @classmethod
    def _validate_difficulty_distribution(cls, test_cases: List[Dict[str, Any]], easy_count: int, medium_count: int, hard_count: int) -> Dict[str, Any]:
        """
        Validates that test cases match target difficulty distribution.
        Allows 20% tolerance due to LLM variability.
        """
        from collections import Counter

        actual_dist = Counter(tc["difficulty"] for tc in test_cases)
        actual_easy = actual_dist.get("Easy", 0)
        actual_medium = actual_dist.get("Medium", 0)
        actual_hard = actual_dist.get("Hard", 0)

        total = len(test_cases)
        tolerance = max(1, int(total * 0.2))  # 20% tolerance

        is_valid = (
            abs(actual_easy - easy_count) <= tolerance and
            abs(actual_medium - medium_count) <= tolerance and
            abs(actual_hard - hard_count) <= tolerance
        )

        return {
            "is_valid": is_valid,
            "target": {"Easy": easy_count, "Medium": medium_count, "Hard": hard_count},
            "actual": {"Easy": actual_easy, "Medium": actual_medium, "Hard": actual_hard},
            "tolerance": tolerance
        }

    @classmethod
    def _derive_dynamic_categories(cls, department: str, task_type: str, prompt: str) -> List[str]:
        lower = prompt.lower()
        dept_lower = department.lower()
        task_lower = task_type.lower()

        if "code" in lower or "software" in dept_lower or "jwt" in lower or "api" in lower or "develop" in task_lower:
            return [
                "Authentication Flow",
                "API Specification",
                "Security & Tokens",
                "Error Handling & Exceptions",
                "Edge Case Inputs",
                "Architecture & Middleware",
                "Performance & Concurrency",
                "Configuration & Env"
            ]
        elif "json" in lower or "extract" in task_lower or "data" in dept_lower:
            return [
                "Complete Data Record",
                "Missing Field",
                "Nested Schema",
                "Multiple Records",
                "Invalid Payload",
                "Duplicate Information",
                "Boundary Condition"
            ]
        elif "email" in lower or "communication" in task_lower or "support" in dept_lower or "customer" in task_lower:
            return [
                "Formal Direct Inquiry",
                "Urgent Follow-Up",
                "Customer Complaint",
                "Policy Clarification",
                "Short Response",
                "Multi-Party Escalation",
                "Difficult Recipient Context"
            ]
        elif "research" in task_lower or "analysis" in task_lower or "finance" in dept_lower or "market" in lower:
            return [
                "Comparative Research",
                "Multi-Factor Analysis",
                "Conflicting Market Data",
                "Missing Historical Metrics",
                "Executive Summary",
                "Risk & Scenario Modeling",
                "Regulatory Compliance"
            ]
        elif "content" in task_lower or "marketing" in dept_lower or "copy" in lower or "doc" in lower:
            return [
                "Technical Documentation",
                "Getting Started Guide",
                "API Reference Walkthrough",
                "Security Best Practices",
                "Troubleshooting Guide",
                "Migration & Versioning",
                "FAQ & Common Pitfalls"
            ]
        else:
            return [
                "Standard Core Workflow",
                "Complex Multi-Requirement",
                "Boundary & Edge Case",
                "Format & Constraint Verification",
                "Missing Data Recovery",
                "High-Volume / Scalability",
                "Domain Compliance"
            ]
