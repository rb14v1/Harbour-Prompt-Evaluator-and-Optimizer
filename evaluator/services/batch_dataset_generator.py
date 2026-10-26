import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from .dataset_generator import DatasetGenerator
from .dataset_validator import DatasetValidator
from .scorer import Scorer

logger = logging.getLogger(__name__)


class BatchDatasetGenerator:
    """
    Generates the additional datasets for one prompt (indexes 2..N).
    Dataset 1 comes from the LangGraph pipeline and is not regenerated here.
    """

    MAX_WORKERS = 50

    @classmethod
    def generate_additional(
        cls,
        department: str,
        task_type: str,
        original_prompt: str,
        processed_prompt: str,
        analysis: Dict[str, Any],
        dataset_size: int,
        prompt_id: str,
        num_datasets: int
    ) -> List[Dict[str, Any]]:
        if num_datasets <= 1:
            return []

        indexes = list(range(2, num_datasets + 1))

        def build(index: int) -> Dict[str, Any]:
            raw = DatasetGenerator.generate(
                department=department,
                task_type=task_type,
                original_prompt=original_prompt,
                processed_prompt=processed_prompt,
                analysis=analysis,
                dataset_size=dataset_size,
                prompt_id=prompt_id,
                variation_index=index,
                variation_total=num_datasets
            )
            validated, validation_summary = DatasetValidator.validate_and_repair(
                dataset=raw,
                target_size=dataset_size,
                department=department,
                task_type=task_type,
                prompt=original_prompt,
                prompt_id=prompt_id
            )
            dataset_summary = Scorer.calculate_dataset_summary(
                dataset=validated,
                prompt_id=prompt_id,
                department=department,
                task_type=task_type
            )
            return {
                "dataset_index": index,
                "dataset": validated,
                "validation_summary": validation_summary,
                "dataset_summary": dataset_summary
            }

        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as executor:
            futures = [(index, executor.submit(build, index)) for index in indexes]
            for index, future in futures:
                try:
                    results.append(future.result())
                except Exception:
                    logger.exception(f"Failed to generate dataset {index} for {prompt_id}")

        logger.info(f"Generated {len(results)}/{len(indexes)} additional datasets for {prompt_id}")
        return results
