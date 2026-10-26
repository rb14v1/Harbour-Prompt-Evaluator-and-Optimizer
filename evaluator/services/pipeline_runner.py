import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, Iterator, Tuple

from . import langgraph_workflow as wf

STEP_OF_JOB = {"eval": "eval", "gen": "gen", "extra": "gen", "val": "val", "reeval": "reeval"}


def _delta(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in after.items() if k not in before or before[k] is not v}


def _validate_and_grade(state: Dict[str, Any]) -> Dict[str, Any]:
    return wf.test_case_validator_node(wf.dataset_validator_node(state))


def _run_parallel(jobs: Dict[str, Tuple[Callable, Dict[str, Any]]]) -> Iterator[Tuple[str, Any, float]]:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        futures = {executor.submit(fn, snapshot): key for key, (fn, snapshot) in jobs.items()}
        for future in as_completed(futures):
            yield futures[future], future.result(), round(time.perf_counter() - start, 3)


def _run_parallel_steps(jobs: Dict[str, Tuple[Callable, Dict[str, Any]]], outputs: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
    pending = Counter(STEP_OF_JOB[key] for key in jobs)
    for step in pending:
        yield {"event": "start", "step": step}
    for key, output, elapsed in _run_parallel(jobs):
        outputs[key] = output
        step = STEP_OF_JOB[key]
        pending[step] -= 1
        if pending[step] == 0:
            yield {"event": "done", "step": step, "duration": elapsed}


def run_evaluation_pipeline(
    department: str,
    task_type: str,
    prompt: str,
    dataset_size: int,
    prompt_id: str,
    num_datasets: int
) -> Iterator[Dict[str, Any]]:
    """
    Runs the same nodes as the LangGraph workflow, in the same order, and yields a
    start/done event around each agent. Independent agents run concurrently:
    evaluator | dataset 1 | datasets 2..N, then validation | re-validation.
    Yields a final {"event": "result", "state": ...} with the full workflow state.
    """
    state: Dict[str, Any] = {
        "department": department.strip(),
        "task_type": task_type.strip(),
        "original_prompt": prompt.strip(),
        "prompt_id": prompt_id,
        "dataset_size": dataset_size,
        "num_datasets": num_datasets,
        "status": "INITIALIZED"
    }

    yield {"event": "start", "step": "prep"}
    started = time.perf_counter()
    state = {**state, **wf.preprocessor_node(state)}
    yield {"event": "done", "step": "prep", "duration": round(time.perf_counter() - started, 3)}

    yield {"event": "start", "step": "analyze"}
    started = time.perf_counter()
    state = {**state, **wf.analyzer_node(state)}
    yield {"event": "done", "step": "analyze", "duration": round(time.perf_counter() - started, 3)}

    outputs: Dict[str, Any] = {}
    yield from _run_parallel_steps({
        "eval": (wf.evaluator_node, state),
        "gen": (wf.dataset_generator_node, state),
        "extra": (wf.additional_datasets_node, state),
    }, outputs)

    yield {"event": "start", "step": "opt"}
    started = time.perf_counter()
    base = {
        **outputs["eval"],
        "synthetic_dataset": outputs["gen"].get("synthetic_dataset", {}),
        "additional_datasets": outputs["extra"].get("additional_datasets", [])
    }
    evidence = wf._build_dataset_evidence(base)
    state = {**wf.improver_node({**base, "dataset_evidence": evidence}), "dataset_evidence": evidence}
    yield {"event": "done", "step": "opt", "duration": round(time.perf_counter() - started, 3)}

    snapshot = state
    outputs = {}
    yield from _run_parallel_steps({
        "val": (_validate_and_grade, snapshot),
        "reeval": (wf.revalidator_node, snapshot),
    }, outputs)
    state = {
        **state,
        **_delta(snapshot, outputs["val"]),
        **_delta(snapshot, outputs["reeval"])
    }

    state = {**state, **wf.comparison_node(state)}
    yield {"event": "result", "state": state}
