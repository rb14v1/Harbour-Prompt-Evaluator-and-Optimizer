import logging
from typing import Dict, Any, List
from .llm_client import llm_client

logger = logging.getLogger(__name__)

EVALUATION_DIMENSIONS = [
    {"key": "instruction_following", "name": "Instruction Following"},
    {"key": "clarity", "name": "Clarity"},
    {"key": "specificity", "name": "Specificity"},
    {"key": "context_completeness", "name": "Context Completeness"},
    {"key": "output_format", "name": "Output Format"},
    {"key": "constraints", "name": "Constraints"},
    {"key": "robustness", "name": "Robustness"},
    {"key": "ambiguity", "name": "Ambiguity"},  # 10 = unambiguous, 0 = highly ambiguous
    {"key": "safety", "name": "Safety"},
    {"key": "reusability", "name": "Reusability"},
    {"key": "maintainability", "name": "Maintainability"},
    {"key": "llm_friendliness", "name": "LLM Friendliness"},
    {"key": "token_efficiency", "name": "Token Efficiency"},
    {"key": "scalability", "name": "Scalability"},
    {"key": "overall_prompt_design", "name": "Overall Prompt Design"},
]

class Evaluator:
    """
    Evaluates prompts across exactly 15 predefined dimensions using a 0-10 score scale.
    """

    SYSTEM_PROMPT = """You are a Principal Prompt Engineering & LLM Quality Auditor.

MISSION: Evaluate prompt quality AND identify what to test.

CRITICAL: Your evaluation scores directly drive test case generation:
- Dimensions scoring < 5.0 → HARD test cases (edge cases, error handling)
- Dimensions scoring 5-7 → MEDIUM test cases (multi-constraint handling)
- Dimensions scoring > 7 → EASY test cases (basic happy paths)

Your evaluation is not just a score - it's a ROADMAP for improvement.

Your task is to critically evaluate a given prompt across EXACTLY 15 predefined dimensions.

Evaluation Scale (0 to 10):
0 = Very poor | 1-2 = Poor | 3-4 = Weak | 5 = Average | 6-7 = Good | 8-9 = Very good | 10 = Excellent
Higher score MUST ALWAYS represent better prompt quality.

Special Note on Ambiguity:
Score 10 = Highly clear, precise, and essentially unambiguous.
Score 0 = Extremely vague, open-ended, and highly ambiguous.

The 15 dimensions to evaluate are:
1. instruction_following (Clarity and directness of instructions)
2. clarity (Readability, structure, plain language)
3. specificity (Granular details, parameters, edge case definitions)
4. context_completeness (Sufficiency of background, persona, domain info)
5. output_format (Clear specification of expected output format)
6. constraints (Negative constraints, length limits, rules)
7. robustness (Resilience against ambiguous inputs)
8. ambiguity (Degree of freedom from ambiguity: 10 = completely unambiguous)
9. safety (Mitigation of hallucinations, insecure behaviors)
10. reusability (Adaptability across scenarios)
11. maintainability (Modular structure, ease of updates)
12. llm_friendliness (Appropriate delimiters, structured XML/Markdown tags)
13. token_efficiency (Conciseness without losing context)
14. scalability (Ability to handle enterprise workloads)
15. overall_prompt_design (Architectural elegance)

SPEED & CONCISENESS RULE:
Keep each field extremely concise (maximum 1 crisp sentence for reasoning, 1 short sentence for identified_issue, 1 short sentence for recommendation). Keep summary to 1 sentence.

Return your evaluation as a strict JSON object with this structure:
{
  "dimensions": {
    "instruction_following": {
      "score": <int 0-10>,
      "reasoning": "<1 short sentence>",
      "identified_issue": "<1 short sentence>",
      "recommendation": "<1 short sentence>"
    },
    ... (all 15 dimensions strictly present)
  },
  "overall_score": <float 0-10>,
  "summary": "<1-2 sentence executive summary>"
}
"""

    @classmethod
    def evaluate(cls, department: str, task_type: str, prompt: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        user_content = f"""Department: {department}
Task Type: {task_type}
Prompt:
\"\"\"
{prompt}
\"\"\"

Context:
- Intent: {analysis.get('prompt_intent', '')}
- Constraints: {', '.join(analysis.get('constraints', [])[:3])}
- Output Format: {analysis.get('output_format', '')}
"""
        if llm_client.is_configured():
            res = llm_client.generate_json(cls.SYSTEM_PROMPT, user_content, temperature=0.1)
            if res and isinstance(res, dict) and "dimensions" in res:
                dims = res.get("dimensions", {})
                # Ensure all 15 dimensions are present and clamped 0-10
                validated_dims = {}
                total_score = 0
                for item in EVALUATION_DIMENSIONS:
                    k = item["key"]
                    name = item["name"]
                    d_data = dims.get(k, {})
                    score = d_data.get("score", 5)
                    try:
                        score = max(0, min(10, int(score)))
                    except Exception:
                        score = 5
                    reasoning = d_data.get("reasoning", f"Evaluation for {name}")
                    issue = d_data.get("identified_issue", "No critical issue detected.")
                    rec = d_data.get("recommendation", f"Enhance {name.lower()} with explicit guidelines.")
                    validated_dims[k] = {
                        "name": name,
                        "score": score,
                        "reasoning": reasoning,
                        "identified_issue": issue,
                        "recommendation": rec
                    }
                    total_score += score

                overall_score = round(total_score / len(EVALUATION_DIMENSIONS), 1)
                return {
                    "dimensions": validated_dims,
                    "overall_score": overall_score,
                    "summary": res.get("summary", f"Prompt evaluated with an overall score of {overall_score}/10."),
                    "llm_used": True
                }

        # Resilient fallback evaluation based on heuristics
        result = cls._fallback_evaluate(department, task_type, prompt, analysis)
        result["llm_used"] = False
        return result

    @classmethod
    def _fallback_evaluate(cls, department: str, task_type: str, prompt: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        words = len(prompt.split())
        has_format = bool(analysis.get("output_format") and analysis.get("output_format") != "Text / Natural Language")
        has_constraints = len(analysis.get("constraints", [])) > 1
        has_missing = len(analysis.get("missing_information", [])) > 0
        has_ambiguity = len(analysis.get("ambiguities", [])) > 0

        # Baseline heuristic scores
        base_clarity = 7 if words > 15 else 4
        base_spec = 7 if words > 40 else (5 if words > 15 else 3)
        base_inst = 7 if any(kw in prompt.lower() for kw in ["create", "generate", "write", "analyze", "extract", "build"]) else 5
        base_format = 8 if has_format else (5 if "format" in prompt.lower() else 4)
        base_ctx = 6 if words > 30 else 4
        base_const = 7 if has_constraints and ("not" in prompt.lower() or "only" in prompt.lower() or "must" in prompt.lower()) else 4
        base_rob = 5 if words > 25 else 4
        base_amb = 5 if has_ambiguity else 7
        base_safe = 8  # generally safe by default
        base_reuse = 6
        base_maint = 5
        base_llm = 6 if ("#" in prompt or ":" in prompt or "\n" in prompt) else 4
        base_token = 8 if words < 60 else 6
        base_scale = 5
        base_overall = round((base_clarity + base_spec + base_inst + base_format + base_ctx + base_const + base_rob + base_amb + base_safe + base_reuse + base_maint + base_llm + base_token + base_scale) / 14, 1)

        dim_specs = {
            "instruction_following": {
                "score": base_inst,
                "reasoning": f"Prompt provides direct directive for {task_type}, but lacks explicit operational steps.",
                "identified_issue": "Lacks step-by-step sequencing for complex multi-part tasks.",
                "recommendation": "Use numbered action items or phase-based execution instructions."
            },
            "clarity": {
                "score": base_clarity,
                "reasoning": "Core request is understandable, though phrasing could be more structured.",
                "identified_issue": "Dense natural language paragraph instead of structured sections.",
                "recommendation": "Organize using clear markdown headings and bullet points."
            },
            "specificity": {
                "score": base_spec,
                "reasoning": "Mentions primary goal but leaves specific parameters and schemas undefined.",
                "identified_issue": "Missing concrete definitions of acceptable outputs and boundary cases.",
                "recommendation": "Specify explicit input schemas, data types, and target outputs."
            },
            "context_completeness": {
                "score": base_ctx,
                "reasoning": f"Context implies {department} department but omits organizational background.",
                "identified_issue": "Assumes implicit knowledge about audience persona and prerequisites.",
                "recommendation": "Provide background context, target audience, and environment assumptions."
            },
            "output_format": {
                "score": base_format,
                "reasoning": "Output format is implicitly implied rather than rigidly governed.",
                "identified_issue": "No strict schema or response layout defined.",
                "recommendation": "Specify exact output schema (e.g. JSON schema, Markdown template with headers)."
            },
            "constraints": {
                "score": base_const,
                "reasoning": "Very few negative or boundary constraints are provided.",
                "identified_issue": "No explicit limits on length, hallucination prevention, or disallowed terms.",
                "recommendation": "Add a dedicated 'Constraints & Guardrails' section."
            },
            "robustness": {
                "score": base_rob,
                "reasoning": "Vulnerable to variation when presented with edge-case or malformed inputs.",
                "identified_issue": "No error-handling instructions for missing or anomalous input parameters.",
                "recommendation": "Add fallback instructions (e.g. 'If parameter X is missing, return error code Y')."
            },
            "ambiguity": {
                "score": base_amb,
                "reasoning": "Certain adjectives and scope boundaries leave room for LLM subjective interpretation.",
                "identified_issue": "Vague descriptors without quantitative acceptance criteria.",
                "recommendation": "Replace subjective adjectives with measurable criteria and definitions."
            },
            "safety": {
                "score": base_safe,
                "reasoning": "Standard benign prompt intent with low direct risk.",
                "identified_issue": "Lacks explicit instructions to prevent hallucinated data or security leaks.",
                "recommendation": "Instruct LLM to never fabricate facts and avoid disclosing system internals."
            },
            "reusability": {
                "score": base_reuse,
                "reasoning": "Can be adapted with variables but currently hardcodes single-use specifics.",
                "identified_issue": "Input parameters are tightly coupled to static text.",
                "recommendation": "Convert dynamic parameters into template placeholders like {{INPUT_TEXT}}."
            },
            "maintainability": {
                "score": base_maint,
                "reasoning": "Monolithic prompt text is harder to update modularly.",
                "identified_issue": "Instruction, context, and formatting rules are mixed together.",
                "recommendation": "Separate into modular blocks: Role, Context, Task, Constraints, Output Format."
            },
            "llm_friendliness": {
                "score": base_llm,
                "reasoning": "LLM can parse plain text but would benefit from standard delimiter syntax.",
                "identified_issue": "Absence of structured tags (e.g., <context>, <rules>, <input>).",
                "recommendation": "Use XML tags or clear Markdown headers to delineate prompt components."
            },
            "token_efficiency": {
                "score": base_token,
                "reasoning": "Prompt length is compact and reasonably token-efficient.",
                "identified_issue": "Could optimize information density without losing precision.",
                "recommendation": "Maintain concise phrasing while enriching structured constraint definitions."
            },
            "scalability": {
                "score": base_scale,
                "reasoning": "Current design works for single prompt queries, but unproven for batch workloads.",
                "identified_issue": "No batching instructions or standardized machine-readable keys.",
                "recommendation": "Structure outputs with predictable JSON keys for downstream pipeline consumption."
            },
            "overall_prompt_design": {
                "score": int(base_overall),
                "reasoning": f"Prompt provides a functional baseline for {department} {task_type} with clear optimization opportunities.",
                "identified_issue": "Lacks modern prompt engineering architecture (System persona, Few-shot examples, Delimiters).",
                "recommendation": "Adopt a multi-section modular design with strict output formatting and guardrails."
            }
        }

        validated_dims = {}
        total = 0
        for item in EVALUATION_DIMENSIONS:
            k = item["key"]
            name = item["name"]
            spec = dim_specs.get(k, {})
            score = max(0, min(10, spec.get("score", 5)))
            validated_dims[k] = {
                "name": name,
                "score": score,
                "reasoning": spec.get("reasoning", ""),
                "identified_issue": spec.get("identified_issue", ""),
                "recommendation": spec.get("recommendation", "")
            }
            total += score

        overall = round(total / len(EVALUATION_DIMENSIONS), 1)
        return {
            "dimensions": validated_dims,
            "overall_score": overall,
            "summary": f"Evaluated across all 15 dimensions with an overall score of {overall}/10. Key improvement areas: Output Format, Constraints, and Robustness."
        }
