from typing import Dict, Any

from evaluator.agents.preprocessor import PreprocessorAgent
from evaluator.agents.classifier import ClassifierAgent
from evaluator.agents.analyzer import AnalyzerAgent
from evaluator.agents.validator import ValidatorAgent
from evaluator.agents.scoring_engine import ScoringEngine
from evaluator.agents.improver import ImproverAgent
from evaluator.agents.report import ReportAgent
from evaluator.config import QUALITY_THRESHOLD, MAX_ITERATIONS


class PromptEvaluationOrchestrator:
    """
    Orchestrates the complete prompt evaluation and optimization pipeline.

    Workflow:
        Preprocess
            ↓
        Classify
            ↓
        Analyze
            ↓
        Validate
            ↓
        Score
            ↓
        Score >= threshold?
          YES → Ready → Report
          NO  → Improve → Re-analyze → Re-validate → Re-score
                                      ↓
                              Score >= threshold?
                                      ↓
                              YES → Ready → Report
                              NO  → Continue until max iterations
    """

    MAX_ITERATIONS = MAX_ITERATIONS
    THRESHOLD = QUALITY_THRESHOLD

    def __init__(self, max_iterations: int = None, threshold: float = None):
        self.max_iterations = (
            max_iterations
            if max_iterations is not None
            else MAX_ITERATIONS
        )

        self.threshold = (
            threshold
            if threshold is not None
            else QUALITY_THRESHOLD
        )

        # Initialize agents
        self.preprocessor = PreprocessorAgent()
        self.classifier = ClassifierAgent()
        self.analyzer = AnalyzerAgent()
        self.validator = ValidatorAgent()
        self.scoring_engine = ScoringEngine(threshold=self.threshold)
        self.improver = ImproverAgent()
        self.report_agent = ReportAgent()

    def evaluate(self, raw_prompt: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the complete prompt evaluation pipeline.

        The original prompt is never modified.

        Optimization happens only when the score is below the
        configured threshold.

        Args:
            raw_prompt: Raw user prompt
            metadata: User metadata (user_role, task_type, output_format)

        Returns:
            Complete evaluation report.
        """
        if metadata is None:
            metadata = {}

        # Stage 1: Preprocess
        preprocessed = self.preprocessor.process(raw_prompt)

        prompt_id = preprocessed["prompt_id"]
        processed_prompt = preprocessed["processed_prompt"]

        execution_history = {
            "iterations": [
                {
                    "iteration": 0,
                    "stages": {}
                }
            ]
        }

        execution_history["iterations"][0]["stages"]["preprocessor"] = {
            "input": raw_prompt,
            "output": preprocessed
        }

        # Stage 2: Classify (or use provided task_type from metadata)
        if metadata.get("task_type"):
            # User provided task_type - use it directly
            task_type = metadata.get("task_type")
            classification = {
                "task_type": task_type,
                "complexity": metadata.get("complexity", "Moderate"),
                "confidence": 1.0,
                "reasoning": f"User-provided task type: {task_type}",
                "classification_method": "user_provided"
            }
            print(f"[CLASSIFIER] Using user-provided task type: {task_type}")
        else:
            # Auto-detect task_type using classifier
            classification = self.classifier.classify(processed_prompt)

        execution_history["iterations"][0]["stages"]["classifier"] = {
            "input": preprocessed,
            "output": classification
        }

        # Stage 3: Analyze
        analysis = self.analyzer.analyze(
            processed_prompt,
            task_type=classification.get("task_type")
        )

        execution_history["iterations"][0]["stages"]["analyzer"] = {
            "input": classification,
            "output": analysis
        }

        # Stage 4-5: Validate and Score
        validation = self.validator.validate(processed_prompt, analysis, metadata=metadata)
        initial_scoring = self.scoring_engine.calculate_scores(validation)

        execution_history["iterations"][0]["stages"]["validator"] = {
            "input": analysis,
            "output": validation
        }

        # Stage 5: Score
        initial_scoring = self.scoring_engine.calculate_scores(
            validation
        )

        execution_history["iterations"][0]["stages"]["scoring"] = {
            "input": validation,
            "output": initial_scoring
        }

        # Keep the initial evaluation unchanged
        initial_evaluation = {
            "validation": validation,
            "dimension_scores": initial_scoring["dimension_scores"],
            "overall_score": initial_scoring["overall_score"],
            "status": initial_scoring["status"],
            "low_scoring_dimensions": initial_scoring[
                "low_scoring_dimensions"
            ]
        }

        current_prompt = processed_prompt
        current_analysis = analysis
        current_validation = validation
        current_evaluation = initial_scoring

        best_prompt = processed_prompt
        best_analysis = analysis
        best_validation = validation
        best_evaluation = initial_scoring

        best_score = initial_scoring["overall_score"]

        improvement_history = []
        iterations_completed = 0
        iteration = 0

        print(f"\n[ORCHESTRATOR] Starting Optimization:")
        print(f"   Initial Score: {best_score:.1f}/10")

        print(f"   Goal: Optimize to best possible version")

        while iteration < self.max_iterations:
            iteration += 1

            # Create new iteration in execution history
            execution_history["iterations"].append({
                "iteration": iteration,
                "stages": {}
            })

            # Add stages from iteration 0 (preprocessor, classifier, analyzer don't change)
            # but copy analyzer and other previous stages for display
            execution_history["iterations"][iteration]["stages"]["preprocessor"] = execution_history["iterations"][0]["stages"]["preprocessor"]
            execution_history["iterations"][iteration]["stages"]["classifier"] = execution_history["iterations"][0]["stages"]["classifier"]
            execution_history["iterations"][iteration]["stages"]["analyzer"] = execution_history["iterations"][0]["stages"]["analyzer"]

            # Improve prompt
            improvement = self.improver.improve(
                original_prompt=current_prompt,
                analysis=analysis,
                validation=validation,
                scoring=current_evaluation,
                iteration=iteration,
                metadata=metadata
            )

            execution_history["iterations"][iteration]["stages"]["improver"] = {
                "input": {
                    "prompt": current_prompt,
                    "analysis": current_analysis,
                    "validation": current_validation,
                    "scoring": current_evaluation
                },
                "output": improvement
            }

            improvement_history.append(improvement)

            # ----------------------------------------------------
            # CHECK IMPROVEMENT RESULT
            # ----------------------------------------------------

            if not improvement.get("intent_preserved", False):

                print(
                    "[ORCHESTRATOR] "
                    "Intent preservation check failed."
                )
                print(
                    "[ORCHESTRATOR] "
                    "Stopping optimization."
                )

                break

            improved_prompt = improvement.get(
                "improved_prompt",
                ""
            ).strip()

            if not improved_prompt:

                print(
                    "[ORCHESTRATOR] "
                    "Improver returned an empty prompt."
                )
                print(
                    "[ORCHESTRATOR] "
                    "Stopping optimization."
                )

                break

            current_prompt = improvement["improved_prompt"]
            improvement_history.append(improvement)

            # Re-validate improved prompt
            validation = self.validator.validate(current_prompt, analysis, metadata=metadata)
            current_evaluation = self.scoring_engine.calculate_scores(validation)

            # Only accept improvement if score actually increased
            new_score = current_evaluation["overall_score"]
            score_improvement = new_score - best_score

            if new_score > best_score:

                print(
                    "[ORCHESTRATOR] "
                    "Improvement accepted."
                )

                iterations_completed += 1

                best_score = new_score
                best_prompt = improved_prompt
                best_analysis = analysis
                best_validation = validation
                best_evaluation = current_evaluation

                current_prompt = improved_prompt
                current_analysis = analysis
                current_validation = validation
                current_evaluation = current_evaluation

            else:

                print(
                    "[ORCHESTRATOR] "
                    "No score improvement. "
                    "Keeping previous best version."
                )

                # Keep current/best version unchanged
                current_prompt = best_prompt
                current_analysis = best_analysis
                current_validation = best_validation
                current_evaluation = best_evaluation

            # ----------------------------------------------------
            # STOP IMMEDIATELY WHEN THRESHOLD IS REACHED
            # ----------------------------------------------------

            if best_score >= self.threshold:

                print(
                    f"[ORCHESTRATOR] "
                    f"Threshold reached: "
                    f"{best_score:.2f} >= "
                    f"{self.threshold:.2f}"
                )

                print(
                    "[ORCHESTRATOR] "
                    "Stopping optimization."
                )

                break

        else:

            print(
                "[ORCHESTRATOR] "
                "Maximum optimization iterations reached."
            )

        # ============================================================
        # FINAL EVALUATION
        # ============================================================

        final_evaluation = dict(best_evaluation)

        final_score = final_evaluation.get(
            "overall_score",
            best_score
        )

        # ------------------------------------------------------------
        # FINAL STATUS
        #
        # REQUIRED BUSINESS RULE:
        #
        # >= 7.0  -> Ready
        # <  7.0  -> Needs Manual Review
        # ------------------------------------------------------------

        if final_score >= self.threshold:
            final_status = "Ready"
        else:
            final_status = "Needs Manual Review"

        final_evaluation["overall_score"] = final_score
        final_evaluation["status"] = final_status
        final_evaluation["iterations_completed"] = iterations_completed

        print("\n" + "=" * 60)
        print("[ORCHESTRATOR] Final Result")
        print("=" * 60)
        print(f"Final Score : {final_score:.2f}/10")
        print(f"Status      : {final_status}")
        print(
            f"Iterations  : {iterations_completed}"
        )
        print("=" * 60)

        # ============================================================
        # REPORT
        # ============================================================

        report = self.report_agent.generate_report(
            prompt_id=prompt_id,
            original_prompt=raw_prompt,
            classification=classification,
            analysis=best_analysis,
            initial_evaluation=initial_evaluation,
            improvement_history=improvement_history,
            final_evaluation=final_evaluation,
            iterations_required=iterations_completed
        )

        # Add report stage to execution history
        report_output = {
            key: value
            for key, value in report.items()
            if key != "execution_history"
        }

        execution_history["iterations"][0]["stages"]["report"] = {
            "input": {
                "classification": classification,
                "analysis": best_analysis,
                "initial_evaluation": initial_evaluation,
                "improvement_history": improvement_history,
                "final_evaluation": final_evaluation
            },
            "output": report_output
        }

        # Attach execution history to final report
        report["execution_history"] = execution_history

        return report

    def batch_evaluate(self, prompts: list) -> list:
        """
        Evaluate multiple prompts.

        Args:
            prompts: List of prompt strings.

        Returns:
            List of evaluation reports.
        """

        results = []

        for prompt in prompts:

            try:

                result = self.evaluate(prompt)
                results.append(result)

            except Exception as e:

                results.append(
                    {
                        "error": str(e),
                        "prompt": prompt
                    }
                )

        return results