from typing import Dict, Any
from evaluator.agents.preprocessor import PreprocessorAgent
from evaluator.agents.classifier import ClassifierAgent
from evaluator.agents.analyzer import AnalyzerAgent
from evaluator.agents.validator import ValidatorAgent
from evaluator.agents.scoring_engine import ScoringEngine
from evaluator.agents.improver import ImproverAgent
from evaluator.agents.report import ReportAgent

class PromptEvaluationOrchestrator:
    """
    Orchestrates the complete prompt evaluation pipeline.
    """

    MAX_ITERATIONS = 3
    THRESHOLD = 7.0

    def __init__(self, max_iterations: int = 3, threshold: float = 7.0):
        self.max_iterations = max_iterations
        self.threshold = threshold

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

        # Stage 2: Classify
        classification = self.classifier.classify(processed_prompt)

        # Stage 3: Analyze
        analysis = self.analyzer.analyze(
            processed_prompt,
            task_type=classification.get("task_type")
        )

        # Stage 4-5: Validate and Score
        validation = self.validator.validate(processed_prompt, analysis)
        initial_scoring = self.scoring_engine.calculate_scores(validation)

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
        iteration = 0

        while (
            current_evaluation["overall_score"] < self.threshold
            and iteration < self.max_iterations
        ):
            iteration += 1

            # Improve prompt
            improvement = self.improver.improve(
                original_prompt=current_prompt,
                analysis=analysis,
                validation=validation,
                scoring=current_evaluation,
                iteration=iteration
            )

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

        # Final evaluation
        final_evaluation = current_evaluation

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
