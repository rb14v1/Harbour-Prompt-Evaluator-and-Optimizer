from typing import Dict, Any, List
import os

class ScoringEngine:
    """
    Converts validation results to numerical scores and determines next action.
    """

    THRESHOLD = 7.0
    QUALITY_SCORES = {
        "Poor": 2.5,
        "Moderate": 5.0,
        "Good": 7.5,
        "Excellent": 10.0
    }

    def __init__(self, threshold: float = None):
        self.name = "Scoring Engine"
        if threshold is None:
            threshold = float(os.getenv('THRESHOLD', 7.0))
        self.threshold = threshold

    def calculate_scores(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate numerical scores from validation results.

        Args:
            validation: Validation output with dimension ratings

        Returns:
            Score breakdown and overall score
        """
        dimension_scores = {}
        validation_data = validation.get("validation", {})

        # Extract and validate dimension scores
        for dimension, data in validation_data.items():
            if isinstance(data, dict) and "score" in data:
                score = float(data["score"])
                # Ensure score is valid
                if score not in self.QUALITY_SCORES.values():
                    score = self._round_to_valid_score(score)
                dimension_scores[dimension] = score
            else:
                dimension_scores[dimension] = 5.0  # Default to Moderate

        # Calculate overall score
        if dimension_scores:
            overall_score = sum(dimension_scores.values()) / len(dimension_scores)
            overall_score = round(overall_score, 2)
        else:
            overall_score = 0.0

        # Identify low and high performing dimensions
        low_scoring = self._get_low_scoring_dimensions(dimension_scores)
        high_performing = self._get_high_performing_dimensions(dimension_scores)

        # Determine status
        status = "Ready" if overall_score >= self.threshold else "Needs Improvement"

        return {
            "dimension_scores": dimension_scores,
            "overall_score": overall_score,
            "threshold": self.threshold,
            "status": status,
            "low_scoring_dimensions": low_scoring,
            "high_performing_dimensions": high_performing
        }

    def should_improve(self, overall_score: float) -> bool:
        """Determine if prompt should be improved."""
        return overall_score < self.threshold

    def _round_to_valid_score(self, score: float) -> float:
        """Round score to nearest valid value."""
        valid_scores = list(self.QUALITY_SCORES.values())
        return min(valid_scores, key=lambda x: abs(x - score))

    def _get_low_scoring_dimensions(self, scores: Dict[str, float], threshold: float = 5.5) -> List[str]:
        """Identify dimensions scoring below threshold."""
        return sorted(
            [dim for dim, score in scores.items() if score < threshold],
            key=lambda x: scores[x]
        )

    def _get_high_performing_dimensions(self, scores: Dict[str, float], threshold: float = 7.0) -> List[str]:
        """Identify dimensions scoring above threshold."""
        return sorted(
            [dim for dim, score in scores.items() if score >= threshold],
            key=lambda x: scores[x],
            reverse=True
        )
