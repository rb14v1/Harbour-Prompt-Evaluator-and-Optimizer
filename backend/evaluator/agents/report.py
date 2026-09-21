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
        # Use threshold from final_evaluation or default to 7.0
        threshold = final_evaluation.get("threshold", 7.0)

        print(f"\n📊 Status Determination:")
        print(f"   Final score: {final_score}")
        print(f"   Threshold: {threshold}")
        print(f"   Status will be: {'Ready' if final_score >= threshold else 'Needs Manual Review'}")

        # Determine final prompt (improved or original)
        final_prompt = original_prompt
        improvements_made = 0

        if improvement_history:
            print(f"\n✅ Improvement History found: {len(improvement_history)} improvements")
            for i, h in enumerate(improvement_history):
                print(f"   Improvement {i}: keys={list(h.keys())}, has_improved_prompt={bool(h.get('improved_prompt'))}")
            final_prompt = improvement_history[-1].get("improved_prompt", original_prompt)
            print(f"   Final prompt set: {bool(final_prompt and final_prompt != original_prompt)}")
            improvements_made = len([h for h in improvement_history if h.get("intent_preserved", True)])
        else:
            print("\n⚠️  No improvement history found - using original prompt")

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
        """Generate executive summary - no thresholds, just facts."""
        if original_prompt == final_prompt:
            # No improvements - already optimal
            return f"✓ Prompt analysis complete. Final score: {final_score:.1f}/10. Status: {status}."
        else:
            # Improvements were made
            score_change = final_score - initial_score
            change_text = f"improved by +{score_change:.2f}" if score_change > 0 else f"adjusted by {score_change:.2f}"
            return f"✓ Prompt optimized in {improvements_made} iteration(s). Score {change_text} (from {initial_score:.1f} to {final_score:.1f}). Status: {status}."

    def format_for_json(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure report is JSON-serializable."""
        return report
