from typing import Dict, Any, List
from datetime import datetime

class ReportAgent:
    """
    Generates comprehensive final reports from evaluation results.
    """

    def __init__(self):
        self.name = "Report Agent"

    def generate_report(
        self,
        prompt_id: str,
        original_prompt: str,
        classification: Dict[str, Any],
        analysis: Dict[str, Any],
        initial_evaluation: Dict[str, Any],
        improvement_history: List[Dict[str, Any]],
        final_evaluation: Dict[str, Any],
        iterations_required: int
    ) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.

        Args:
            prompt_id: Unique prompt identifier
            original_prompt: Original prompt text
            classification: Classification results
            analysis: Analysis results
            initial_evaluation: Initial validation and scoring
            improvement_history: List of improvement iterations
            final_evaluation: Final validation and scoring
            iterations_required: Number of iterations used

        Returns:
            Comprehensive final report
        """
        final_score = final_evaluation.get("overall_score", 0.0)
        threshold = final_evaluation.get("threshold", 7.0)

        # Determine final prompt (improved or original)
        final_prompt = original_prompt
        improvements_made = 0

        if improvement_history:
            final_prompt = improvement_history[-1].get("improved_prompt", original_prompt)
            improvements_made = len([h for h in improvement_history if h.get("intent_preserved", True)])

        # Determine status
        status = "Ready" if final_score >= threshold else "Needs Manual Review"

        # Generate summary
        summary = self._generate_summary(
            original_prompt,
            final_prompt,
            initial_evaluation.get("overall_score", 0.0),
            final_score,
            improvements_made,
            status
        )

        initial_score = initial_evaluation.get("overall_score", 0.0)

        report = {
            "prompt_id": prompt_id,
            "original_prompt": original_prompt,
            "initial_score": initial_score,
            "final_score": final_score,
            "classification": classification,
            "analysis": analysis,
            "initial_evaluation": {
                "dimension_scores": initial_evaluation.get("dimension_scores", {}),
                "overall_score": initial_score,
                "status": initial_evaluation.get("status", "Unknown"),
                "low_scoring_dimensions": initial_evaluation.get("low_scoring_dimensions", [])
            },
            "improvement_history": improvement_history,
            "final_evaluation": {
                "dimension_scores": final_evaluation.get("dimension_scores", {}),
                "overall_score": final_score,
                "status": final_evaluation.get("status", "Unknown"),
                "high_performing_dimensions": final_evaluation.get("high_performing_dimensions", [])
            },
            "final_prompt": final_prompt,
            "summary": summary,
            "status": status,
            "improvements_made": improvements_made,
            "iterations_required": iterations_required,
            "timestamp": datetime.utcnow().isoformat()
        }

        return report

    def _generate_summary(
        self,
        original_prompt: str,
        final_prompt: str,
        initial_score: float,
        final_score: float,
        improvements_made: int,
        status: str
    ) -> str:
        """Generate executive summary of evaluation."""
        if original_prompt == final_prompt:
            # No improvements needed
            if final_score >= 7.0:
                return f"Excellent prompt. Score: {final_score}/10.0. Ready for immediate use with no improvements needed."
            else:
                return f"Prompt score: {final_score}/10.0. Does not meet quality threshold ({7.0}). Manual review recommended."
        else:
            # Improvements made
            score_change = final_score - initial_score
            change_text = f"improved by {abs(score_change):.2f}" if score_change > 0 else f"decreased by {abs(score_change):.2f}"
            return f"Prompt {change_text} points (from {initial_score:.2f} to {final_score:.2f}) over {improvements_made} iteration(s). Status: {status}."

    def format_for_json(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure report is JSON-serializable."""
        return report
