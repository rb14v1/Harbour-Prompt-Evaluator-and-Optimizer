from typing import Dict, Any, List

class Scorer:
    """
    Computes summary score metrics, difficulty breakdowns, category distributions,
    and dimension score aggregations.
    """

    @staticmethod
    def calculate_overall_score(dimensions: Dict[str, Any]) -> float:
        if not dimensions:
            return 0.0
        scores = []
        for dim_key, data in dimensions.items():
            if isinstance(data, dict) and "score" in data:
                try:
                    scores.append(float(data["score"]))
                except (ValueError, TypeError):
                    pass
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 1)

    @staticmethod
    def calculate_dataset_summary(dataset: Dict[str, Any], prompt_id: str = "PROMPT-001", department: str = "", task_type: str = "") -> Dict[str, Any]:
        test_cases = dataset.get("test_cases", []) if isinstance(dataset, dict) else []
        total = len(test_cases)

        difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
        category_counts = {}
        edge_case_count = 0

        for tc in test_cases:
            diff = tc.get("difficulty", "Medium")
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

            cat = tc.get("category", "General")
            category_counts[cat] = category_counts.get(cat, 0) + 1

            if tc.get("edge_case", False) or diff == "Hard":
                edge_case_count += 1

        return {
            "prompt_id": prompt_id,
            "department": department,
            "task_type": task_type,
            "dataset_size": total,
            "difficulty_distribution": difficulty_counts,
            "category_distribution": category_counts,
            "edge_cases_count": edge_case_count,
            "easy_percentage": round((difficulty_counts["Easy"] / total * 100), 1) if total > 0 else 0,
            "medium_percentage": round((difficulty_counts["Medium"] / total * 100), 1) if total > 0 else 0,
            "hard_percentage": round((difficulty_counts["Hard"] / total * 100), 1) if total > 0 else 0,
        }

    @staticmethod
    def _overall_status(difference: float) -> str:
        if difference >= 1.0:
            return "successful"
        if difference >= 0.5:
            return "moderate"
        if difference > 0:
            return "minimal"
        return "no improvement"

    @staticmethod
    def _dimension_status(difference: float) -> str:
        if difference > 0.5:
            return "improved"
        if difference < -0.5:
            return "regressed"
        return "maintained"

    @staticmethod
    def compare_evaluations(original_eval: Dict[str, Any], improved_eval: Dict[str, Any]) -> Dict[str, Any]:
        # Use overall scores directly (most accurate)
        orig_overall = original_eval.get("overall_score", 0.0)
        imp_overall = improved_eval.get("overall_score", 0.0)

        # Calculate net elevation
        total_diff = round(imp_overall - orig_overall, 1)

        orig_dims = original_eval.get("dimensions", {})
        imp_dims = improved_eval.get("dimensions", {})

        comparison_dims = {}
        regressions = []

        for key, orig_data in orig_dims.items():
            name = orig_data.get("name", key.replace("_", " ").title())
            orig_score = orig_data.get("score", 0)
            imp_data = imp_dims.get(key, {})
            imp_score = imp_data.get("score", orig_score)
            diff = imp_score - orig_score
            dim_status = Scorer._dimension_status(diff)
            if dim_status == "regressed":
                regressions.append(name)

            comparison_dims[key] = {
                "name": name,
                "original_score": orig_score,
                "improved_score": imp_score,
                "difference": diff,
                "status": dim_status,
                "percentage_change": round((diff / max(1, orig_score)) * 100, 1) if orig_score > 0 else 0,
                "original_issue": orig_data.get("identified_issue", ""),
                "resolution": imp_data.get("reasoning", "Addressed in optimized prompt architecture.")
            }

        return {
            "original_overall_score": orig_overall,
            "improved_overall_score": imp_overall,
            "overall_difference": total_diff,
            "status": Scorer._overall_status(total_diff),
            "regressions": regressions,
            "dimensions_comparison": comparison_dims,
            "key_improvements": [
                f"Increased {v['name']} by +{v['difference']} points"
                for v in comparison_dims.values() if v['difference'] > 0
            ]
        }
