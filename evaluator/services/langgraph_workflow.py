import logging
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from .preprocessor import Preprocessor
from .analyzer import Analyzer
from .evaluator import Evaluator
from .dataset_generator import DatasetGenerator
from .dataset_validator import DatasetValidator
from .scorer import Scorer
from .improver import Improver
from .revalidator import Revalidator
from .llm_case_grader import LLMCaseGrader
from .batch_dataset_generator import BatchDatasetGenerator

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict, total=False):
    # Inputs
    department: str
    task_type: str
    original_prompt: str
    processed_prompt: str
    prompt_id: str
    dataset_size: int
    num_datasets: int

    # Core artifacts
    analysis: Dict[str, Any]
    evaluation: Dict[str, Any]
    synthetic_dataset: Dict[str, Any]
    validation_summary: Dict[str, Any]
    dataset_summary: Dict[str, Any]
    additional_datasets: List[Dict[str, Any]]
    all_datasets: List[Dict[str, Any]]
    dataset_evidence: str

    # Improvement artifacts
    improved_prompt: str
    improvement_metadata: Dict[str, Any]
    test_case_validation: Dict[str, Any]
    re_evaluation: Dict[str, Any]
    comparison: Dict[str, Any]

    # Metrics
    overall_original_score: float
    overall_improved_score: float
    score_difference: float

    # Status & Errors
    status: str
    error: Optional[str]


def preprocessor_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing Preprocessor Node...")
    prep_res = Preprocessor.process(state.get("original_prompt", ""))
    return {
        **state,
        "processed_prompt": prep_res["processed_prompt"]
    }


def analyzer_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing Analyzer Node...")
    dept = state.get("department", "General")
    task = state.get("task_type", "General Task")
    orig = state.get("original_prompt", "")
    proc = state.get("processed_prompt", orig)

    analysis_res = Analyzer.analyze(
        department=dept,
        task_type=task,
        original_prompt=orig,
        processed_prompt=proc
    )
    return {
        **state,
        "analysis": analysis_res
    }


def evaluator_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing 15-Dimension Evaluator Node...")
    dept = state.get("department", "General")
    task = state.get("task_type", "General Task")
    proc = state.get("processed_prompt", state.get("original_prompt", ""))
    analysis = state.get("analysis", {})

    eval_res = Evaluator.evaluate(
        department=dept,
        task_type=task,
        prompt=proc,
        analysis=analysis
    )
    return {
        **state,
        "evaluation": eval_res,
        "overall_original_score": eval_res.get("overall_score", 0.0)
    }


def dataset_generator_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing Synthetic Dataset Generator Node...")
    dept = state.get("department", "General")
    task = state.get("task_type", "General Task")
    orig = state.get("original_prompt", "")
    proc = state.get("processed_prompt", orig)
    analysis = state.get("analysis", {})
    size = state.get("dataset_size", 5)
    pid = state.get("prompt_id", "PROMPT-001")

    dataset_res = DatasetGenerator.generate(
        department=dept,
        task_type=task,
        original_prompt=orig,
        processed_prompt=proc,
        analysis=analysis,
        dataset_size=size,
        prompt_id=pid
    )
    return {
        **state,
        "synthetic_dataset": dataset_res
    }


def _build_dataset_evidence(state: WorkflowState) -> str:
    datasets = [{"dataset": state.get("synthetic_dataset", {})}] + state.get("additional_datasets", [])
    original = state.get("processed_prompt") or state.get("original_prompt", "")
    grades_per_dataset = LLMCaseGrader.grade_datasets(original, datasets)
    cases = [
        {**tc, **grade}
        for item, grades in zip(datasets, grades_per_dataset)
        for tc, grade in zip(item["dataset"].get("test_cases", []), grades)
    ]
    summary = LLMCaseGrader.summarise(cases)
    if summary["graded_cases"] == 0:
        return ""

    failing_cases = [tc for tc in cases if tc.get("llm_verdict") == "FAIL"]
    failing_by_category = {}
    failing_samples = []
    for tc in failing_cases:
        category = tc.get("category", "General")
        failing_by_category[category] = failing_by_category.get(category, 0) + 1
        if len(failing_samples) < 10:
            failing_samples.append(
                f"- {tc.get('test_case_id', 'TC-???')} [{tc.get('difficulty', 'Unknown')}] "
                f"{category}: {str(tc.get('input', ''))[:200]}"
            )

    top_categories = sorted(failing_by_category.items(), key=lambda kv: kv[1], reverse=True)[:10]
    lines = [
        f"Datasets: {len(datasets)} | Test cases: {len(cases)}",
        f"Original prompt failed {len(failing_cases)} of {summary['graded_cases']} graded cases "
        f"({summary['pass_rate']:.1f}% pass rate).",
        "Failing categories: " + (", ".join(f"{c} ({n})" for c, n in top_categories) or "none"),
        "Sample failing cases:",
        *(failing_samples or ["- none"])
    ]
    return "\n".join(lines)


def parallel_stage_node(state: WorkflowState) -> WorkflowState:
    """
    Runs the evaluator, dataset 1 and datasets 2..N in parallel, then builds
    dataset evidence from all datasets and runs the improver with it.
    """
    from concurrent.futures import ThreadPoolExecutor
    logger.info("Executing Parallel Stage (evaluate | datasets 1..N)...")

    with ThreadPoolExecutor(max_workers=3) as executor:
        eval_future = executor.submit(evaluator_node, state)
        ds_future = executor.submit(dataset_generator_node, state)
        extra_future = executor.submit(additional_datasets_node, state)

        eval_state = eval_future.result()
        ds_state = ds_future.result()
        extra_state = extra_future.result()

    base = {
        **eval_state,
        "synthetic_dataset": ds_state.get("synthetic_dataset", {}),
        "additional_datasets": extra_state.get("additional_datasets", [])
    }
    evidence = _build_dataset_evidence(base)
    improved = improver_node({**base, "dataset_evidence": evidence})
    return {**improved, "dataset_evidence": evidence}


def dataset_validator_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing Dataset Validator Node...")
    raw_dataset = state.get("synthetic_dataset", {})
    size = state.get("dataset_size", 5)
    dept = state.get("department", "General")
    task = state.get("task_type", "General Task")
    orig = state.get("original_prompt", "")
    pid = state.get("prompt_id", "PROMPT-001")

    validated_dataset, validation_summary = DatasetValidator.validate_and_repair(
        dataset=raw_dataset,
        target_size=size,
        department=dept,
        task_type=task,
        prompt=orig,
        prompt_id=pid
    )

    dataset_summary = Scorer.calculate_dataset_summary(
        dataset=validated_dataset,
        prompt_id=pid,
        department=dept,
        task_type=task
    )

    return {
        **state,
        "synthetic_dataset": validated_dataset,
        "validation_summary": validation_summary,
        "dataset_summary": dataset_summary
    }


def additional_datasets_node(state: WorkflowState) -> Dict[str, Any]:
    logger.info("Executing Additional Datasets Node...")
    additional = BatchDatasetGenerator.generate_additional(
        department=state.get("department", "General"),
        task_type=state.get("task_type", "General Task"),
        original_prompt=state.get("original_prompt", ""),
        processed_prompt=state.get("processed_prompt", state.get("original_prompt", "")),
        analysis=state.get("analysis", {}),
        dataset_size=state.get("dataset_size", 5),
        prompt_id=state.get("prompt_id", "PROMPT-001"),
        num_datasets=state.get("num_datasets", 1)
    )
    return {"additional_datasets": additional}


def improver_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing Improver Node...")
    dept = state.get("department", "General")
    task = state.get("task_type", "General Task")
    orig = state.get("original_prompt", "")
    proc = state.get("processed_prompt", orig)
    analysis = state.get("analysis", {})
    evaluation = state.get("evaluation", {})

    improve_res = Improver.improve(
        department=dept,
        task_type=task,
        original_prompt=orig,
        processed_prompt=proc,
        analysis=analysis,
        evaluation=evaluation,
        dataset_evidence=state.get("dataset_evidence", "")
    )
    return {
        **state,
        "improved_prompt": improve_res["improved_prompt"],
        "improvement_metadata": {
            "explanation_of_changes": improve_res.get("explanation_of_changes", []),
            "structural_sections_added": improve_res.get("structural_sections_added", [])
        }
    }


def test_case_validator_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing LLM Test Case Grader Node...")
    improved_prompt = state.get("improved_prompt", "")
    datasets = [
        {
            "dataset_index": 1,
            "dataset": state.get("synthetic_dataset", {}),
            "validation_summary": state.get("validation_summary", {}),
            "dataset_summary": state.get("dataset_summary", {})
        },
        *state.get("additional_datasets", [])
    ]

    grades_per_dataset = LLMCaseGrader.grade_datasets(improved_prompt, datasets)
    for item, grades in zip(datasets, grades_per_dataset):
        for tc, grade in zip(item["dataset"].get("test_cases", []), grades):
            tc.update(grade)

    all_cases = [tc for item in datasets for tc in item["dataset"].get("test_cases", [])]
    validation_res = LLMCaseGrader.summarise(all_cases)
    validation_res["datasets_evaluated"] = len(datasets)
    validation_res["per_dataset_pass_rates"] = [
        {
            "dataset_index": item["dataset_index"],
            "pass_rate": LLMCaseGrader.summarise(item["dataset"].get("test_cases", []))["pass_rate"]
        }
        for item in datasets
    ]
    return {
        **state,
        "all_datasets": datasets,
        "test_case_validation": validation_res
    }


def revalidator_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing Re-Validator Node...")
    dept = state.get("department", "General")
    task = state.get("task_type", "General Task")
    improved_prompt = state.get("improved_prompt", "")
    original_eval = state.get("evaluation", {})
    analysis = state.get("analysis", {})

    reeval_res = Revalidator.reevaluate(
        department=dept,
        task_type=task,
        improved_prompt=improved_prompt,
        original_evaluation=original_eval,
        analysis=analysis
    )
    return {
        **state,
        "re_evaluation": reeval_res,
        "overall_improved_score": reeval_res.get("overall_score", 0.0)
    }


def comparison_node(state: WorkflowState) -> WorkflowState:
    logger.info("Executing Comparison Node...")
    original_eval = state.get("evaluation", {})
    re_eval = state.get("re_evaluation", {})

    comp_res = Scorer.compare_evaluations(original_eval, re_eval)
    return {
        **state,
        "comparison": comp_res,
        "score_difference": comp_res.get("overall_difference", 0.0),
        "status": "COMPLETED"
    }


def build_workflow_graph():
    """
    Builds and compiles the end-to-end LangGraph pipeline with parallel evaluation.
    """
    workflow = StateGraph(WorkflowState)

    # Add Nodes
    workflow.add_node("preprocess", preprocessor_node)
    workflow.add_node("analyze", analyzer_node)
    workflow.add_node("parallel_stage", parallel_stage_node)
    workflow.add_node("validate_dataset", dataset_validator_node)
    workflow.add_node("test_case_validate", test_case_validator_node)
    workflow.add_node("revalidate", revalidator_node)
    workflow.add_node("compare", comparison_node)

    # Set Entry Point
    workflow.set_entry_point("preprocess")

    # Define Edges with Concurrency
    workflow.add_edge("preprocess", "analyze")
    workflow.add_edge("analyze", "parallel_stage")
    workflow.add_edge("parallel_stage", "validate_dataset")
    workflow.add_edge("validate_dataset", "test_case_validate")
    workflow.add_edge("test_case_validate", "revalidate")
    workflow.add_edge("revalidate", "compare")
    workflow.add_edge("compare", END)

    return workflow.compile()


# Singleton compiled graph
evaluation_graph = build_workflow_graph()


def execute_evaluation_workflow(
    department: str,
    task_type: str,
    prompt: str,
    dataset_size: int = 5,
    prompt_id: str = "PROMPT-001",
    num_datasets: int = 1
) -> Dict[str, Any]:
    """
    Executes the full LangGraph evaluation and synthetic dataset generation workflow.
    """
    initial_state: WorkflowState = {
        "department": department.strip(),
        "task_type": task_type.strip(),
        "original_prompt": prompt.strip(),
        "prompt_id": prompt_id,
        "dataset_size": dataset_size,
        "num_datasets": num_datasets,
        "status": "INITIALIZED"
    }

    try:
        final_state = evaluation_graph.invoke(initial_state)
        return final_state
    except Exception as e:
        logger.exception(f"Error running evaluation workflow: {e}")
        # Fallback execution in case of graph engine issues
        return _execute_direct_workflow(initial_state)


def _execute_direct_workflow(state: WorkflowState) -> Dict[str, Any]:
    """Direct execution fallback without graph wrapper if required."""
    s1 = preprocessor_node(state)
    s2 = analyzer_node(s1)
    s3 = parallel_stage_node(s2)
    s4 = dataset_validator_node(s3)
    s6 = test_case_validator_node(s4)
    s7 = revalidator_node(s6)
    s8 = comparison_node(s7)
    return s8
