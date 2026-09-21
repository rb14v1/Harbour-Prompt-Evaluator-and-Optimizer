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
    Orchestrates the complete prompt evaluation pipeline.
    """

    MAX_ITERATIONS = MAX_ITERATIONS
    THRESHOLD = QUALITY_THRESHOLD

    def __init__(self, max_iterations: int = None, threshold: float = None):
        self.max_iterations = max_iterations if max_iterations is not None else MAX_ITERATIONS
        self.threshold = threshold if threshold is not None else QUALITY_THRESHOLD

        # Initialize agents
        self.preprocessor = PreprocessorAgent()
        self.classifier = ClassifierAgent()
        self.analyzer = AnalyzerAgent()
        self.validator = ValidatorAgent()
        self.scoring_engine = ScoringEngine(threshold=threshold)
        self.improver = ImproverAgent()
        self.report_agent = ReportAgent()

    def evaluate(self, raw_prompt: str) -> Dict[str, Any]:
        """
        Run complete evaluation pipeline on a prompt.

        Args:
            raw_prompt: Raw user prompt

        Returns:
            Complete evaluation report
        """
        # Stage 1: Preprocess
        preprocessed = self.preprocessor.process(raw_prompt)
        prompt_id = preprocessed["prompt_id"]
        processed_prompt = preprocessed["processed_prompt"]

        # Build execution history structure
        execution_history = {
            "iterations": [
                {
                    "iteration": 0,
                    "stages": {}
                }
            ]
        }

        # Add Preprocessor stage
        execution_history["iterations"][0]["stages"]["preprocessor"] = {
            "input": raw_prompt,
            "output": preprocessed
        }

        # Stage 2: Classify
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
        validation = self.validator.validate(processed_prompt, analysis)
        initial_scoring = self.scoring_engine.calculate_scores(validation)

        execution_history["iterations"][0]["stages"]["validator"] = {
            "input": analysis,
            "output": validation
        }

        execution_history["iterations"][0]["stages"]["scoring"] = {
            "input": validation,
            "output": initial_scoring
        }

        # Store initial evaluation
        initial_evaluation = {
            "validation": validation,
            "dimension_scores": initial_scoring["dimension_scores"],
            "overall_score": initial_scoring["overall_score"],
            "status": initial_scoring["status"],
            "low_scoring_dimensions": initial_scoring["low_scoring_dimensions"]
        }

        # Stage 6: Decision and optimization loop
        improvement_history = []
        current_prompt = processed_prompt
        current_evaluation = initial_scoring
        best_score = initial_scoring["overall_score"]
        best_prompt = processed_prompt
        best_validation = validation
        best_evaluation = initial_scoring
        iteration = 0

        while (
            current_evaluation["overall_score"] < self.threshold
            and iteration < self.max_iterations
        ):
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
                iteration=iteration
            )

            execution_history["iterations"][iteration]["stages"]["improver"] = {
                "input": current_evaluation,
                "output": improvement
            }

            # Check if intent was preserved
            if not improvement.get("intent_preserved", False):
                # Skip this iteration but still record it
                improvement_history.append(improvement)
                break

            current_prompt = improvement["improved_prompt"]
            improvement_history.append(improvement)

            # Re-validate improved prompt
            validation = self.validator.validate(current_prompt, analysis)
            current_evaluation = self.scoring_engine.calculate_scores(validation)

            # Only accept improvement if score actually increased
            new_score = current_evaluation["overall_score"]
            score_improvement = new_score - best_score

            if new_score > best_score:
                best_score = new_score
                best_prompt = current_prompt
                best_validation = validation
                best_evaluation = current_evaluation
            else:
                # Score decreased or stayed same - revert to best known version
                current_prompt = best_prompt
                current_evaluation = best_evaluation
                validation = best_validation
                score_improvement = 0

<<<<<<< HEAD
            # Early stopping: only stop if we've tried at least 2 iterations with minimal improvement
            # OR if score already meets threshold
            if best_score >= self.threshold:
                print(f"✅ Score {best_score} meets threshold {self.threshold} - stopping")
                break
            if best_score >= 6.0 and score_improvement < 0.3 and iteration >= 2:
                print(f"⚠️  Minimal improvement ({score_improvement}) after 2+ iterations - stopping")
=======
            # Early stopping: Stop if threshold reached or improvement is small
            # This prevents wasting iterations on tiny improvements
            if best_score >= self.threshold:
                # Threshold met - stop immediately
                break
            elif iteration >= 1 and score_improvement < 0.5:
                # After iteration 1, if improvement < 0.5 points, stop
                break
            elif iteration >= 1:
                # Max 2 iterations - stop after 2nd iteration regardless
>>>>>>> 358dfedfd21eb7648ce4bcf9dfc40114d396bf84
                break

            # Add updated Validator and Scoring to this iteration (using the re-validated results)
            execution_history["iterations"][iteration]["stages"]["validator"] = {
                "input": analysis,
                "output": validation
            }

            execution_history["iterations"][iteration]["stages"]["scoring"] = {
                "input": validation,
                "output": current_evaluation
            }

        # If score >= threshold, add improver as "skipped"
        if iteration == 0 and execution_history["iterations"][0]["stages"]["scoring"]["output"]["overall_score"] >= self.threshold:
            execution_history["iterations"][0]["stages"]["improver"] = {
                "status": "skipped",
                "reason": "prompt already meets threshold"
            }

        # Final evaluation - always use best score found
        final_evaluation = best_evaluation if best_evaluation else current_evaluation

        # Debug: Ensure final_evaluation has overall_score and threshold
        if "overall_score" not in final_evaluation:
            final_evaluation["overall_score"] = best_score
        if "threshold" not in final_evaluation:
            final_evaluation["threshold"] = self.threshold

        # Stage 6b: Generate Report
        report = self.report_agent.generate_report(
            prompt_id=prompt_id,
            original_prompt=raw_prompt,
            classification=classification,
            analysis=analysis,
            initial_evaluation=initial_evaluation,
            improvement_history=improvement_history,
            final_evaluation=final_evaluation,
            iterations_required=iteration
        )

        # Add Report stage output (exclude execution_history to avoid circular reference)
        report_output = {k: v for k, v in report.items() if k != "execution_history"}
        execution_history["iterations"][0]["stages"]["report"] = {
            "input": {
                "classification": classification,
                "analysis": analysis,
                "initial_evaluation": initial_evaluation,
                "improvement_history": improvement_history,
                "final_evaluation": final_evaluation
            },
            "output": report_output
        }

        # Add execution_history to report
        report["execution_history"] = execution_history

        return report

    def batch_evaluate(self, prompts: list) -> list:
        """
        Evaluate multiple prompts.

        Args:
            prompts: List of prompt strings

        Returns:
            List of evaluation reports
        """
        results = []
        for prompt in prompts:
            try:
                result = self.evaluate(prompt)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "prompt": prompt
                })
        return results
