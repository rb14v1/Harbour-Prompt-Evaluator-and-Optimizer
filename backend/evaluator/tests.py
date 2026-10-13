from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from evaluator.models import Prompt, EvaluationResult
from evaluator.orchestrator import PromptEvaluationOrchestrator
from evaluator.agents.preprocessor import PreprocessorAgent
from evaluator.agents.scoring_engine import ScoringEngine


class PreprocessorAgentTestCase(TestCase):
    """Test Preprocessor Agent"""

    def setUp(self):
        self.agent = PreprocessorAgent()

    def test_normalize_whitespace(self):
        """Test that extra whitespace is normalized"""
        raw_prompt = "This   is    a   test   prompt"
        result = self.agent.process(raw_prompt)

        self.assertEqual(result["processed_prompt"], "This is a test prompt")
        self.assertEqual(result["original_prompt"], raw_prompt)

    def test_preserve_original(self):
        """Test that original prompt is preserved"""
        raw_prompt = "  Test prompt with extra spaces  "
        result = self.agent.process(raw_prompt)

        self.assertEqual(result["original_prompt"], raw_prompt)

    def test_metadata_extraction(self):
        """Test metadata extraction"""
        raw_prompt = "Write a function"
        result = self.agent.process(raw_prompt)

        self.assertIn("metadata", result)
        self.assertIn("length", result["metadata"])
        self.assertIn("timestamp", result["metadata"])
        self.assertEqual(result["metadata"]["length"], 3)  # 3 words


class ScoringEngineTestCase(TestCase):
    """Test Scoring Engine"""

    def setUp(self):
        self.engine = ScoringEngine(threshold=7.0)

    def test_score_calculation_excellent(self):
        """Test score calculation for excellent prompt"""
        validation = {
            "validation": {
                "clarity": {"score": 10.0},
                "specificity": {"score": 10.0},
                "context": {"score": 10.0},
                "completeness": {"score": 10.0},
                "requirements": {"score": 10.0},
                "constraints": {"score": 10.0},
                "expected_output": {"score": 10.0},
                "actionability": {"score": 10.0}
            }
        }

        result = self.engine.calculate_scores(validation)

        self.assertEqual(result["overall_score"], 10.0)
        self.assertEqual(result["status"], "Ready")

    def test_score_calculation_poor(self):
        """Test score calculation for poor prompt"""
        validation = {
            "validation": {
                "clarity": {"score": 2.5},
                "specificity": {"score": 2.5},
                "context": {"score": 2.5},
                "completeness": {"score": 2.5},
                "requirements": {"score": 2.5},
                "constraints": {"score": 2.5},
                "expected_output": {"score": 2.5},
                "actionability": {"score": 2.5}
            }
        }

        result = self.engine.calculate_scores(validation)

        self.assertEqual(result["overall_score"], 2.5)
        self.assertEqual(result["status"], "Needs Improvement")

    def test_threshold_comparison(self):
        """Test threshold comparison"""
        validation = {
            "validation": {
                "clarity": {"score": 7.5},
                "specificity": {"score": 7.5},
                "context": {"score": 7.5},
                "completeness": {"score": 7.5},
                "requirements": {"score": 7.5},
                "constraints": {"score": 7.5},
                "expected_output": {"score": 7.5},
                "actionability": {"score": 7.5}
            }
        }

        result = self.engine.calculate_scores(validation)

        self.assertEqual(result["overall_score"], 7.5)
        self.assertEqual(result["status"], "Ready")
        self.assertTrue(result["overall_score"] >= self.engine.threshold)

    def test_low_scoring_dimensions(self):
        """Test identification of low-scoring dimensions"""
        validation = {
            "validation": {
                "clarity": {"score": 10.0},
                "specificity": {"score": 2.5},
                "context": {"score": 7.5},
                "completeness": {"score": 7.5},
                "requirements": {"score": 5.0},
                "constraints": {"score": 7.5},
                "expected_output": {"score": 7.5},
                "actionability": {"score": 2.5}
            }
        }

        result = self.engine.calculate_scores(validation)

        self.assertIn("specificity", result["low_scoring_dimensions"])
        self.assertIn("actionability", result["low_scoring_dimensions"])
        self.assertNotIn("clarity", result["low_scoring_dimensions"])


class PromptModelTestCase(TestCase):
    """Test Prompt model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_create_prompt(self):
        """Test creating a prompt"""
        prompt = Prompt.objects.create(
            user=self.user,
            original_prompt="Test prompt",
            processed_prompt="Test prompt"
        )

        self.assertEqual(prompt.original_prompt, "Test prompt")
        self.assertEqual(prompt.user, self.user)

    def test_prompt_ordering(self):
        """Test prompts are ordered by creation date"""
        prompt1 = Prompt.objects.create(
            user=self.user,
            original_prompt="First",
            processed_prompt="First"
        )
        prompt2 = Prompt.objects.create(
            user=self.user,
            original_prompt="Second",
            processed_prompt="Second"
        )

        prompts = Prompt.objects.all()
        self.assertEqual(prompts.first().original_prompt, "Second")  # Most recent first


class OrchestratorTestCase(TransactionTestCase):
    """
    Test Orchestrator pipeline.
    Note: Uses TransactionTestCase because it tests database transactions.
    Requires Azure OpenAI to be configured.
    """

    def setUp(self):
        self.orchestrator = PromptEvaluationOrchestrator()

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all agents"""
        self.assertIsNotNone(self.orchestrator.preprocessor)
        self.assertIsNotNone(self.orchestrator.classifier)
        self.assertIsNotNone(self.orchestrator.analyzer)
        self.assertIsNotNone(self.orchestrator.validator)
        self.assertIsNotNone(self.orchestrator.scoring_engine)
        self.assertIsNotNone(self.orchestrator.improver)
        self.assertIsNotNone(self.orchestrator.report_agent)

    def test_orchestrator_configuration(self):
        """Test orchestrator configuration"""
        self.assertEqual(self.orchestrator.max_iterations, 3)
        self.assertEqual(self.orchestrator.threshold, 7.0)

    # Note: Full integration tests would require Azure OpenAI credentials
    # These are included but commented out for CI/CD without secrets
    # Uncomment locally with proper .env configuration


class EvaluationResultModelTestCase(TestCase):
    """Test EvaluationResult model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.prompt = Prompt.objects.create(
            user=self.user,
            original_prompt="Test prompt",
            processed_prompt="Test prompt"
        )

    def test_create_evaluation_result(self):
        """Test creating evaluation result"""
        result = EvaluationResult.objects.create(
            prompt=self.prompt,
            original_prompt="Test prompt",
            final_prompt="Improved test prompt",
            initial_score=5.0,
            final_score=8.0,
            improvements_made=1,
            iterations_required=1,
            summary="Prompt improved",
            status="ready",
            full_report={}
        )

        self.assertEqual(result.initial_score, 5.0)
        self.assertEqual(result.final_score, 8.0)
        self.assertEqual(result.status, "ready")

    def test_score_improvement(self):
        """Test score improvement tracking"""
        result = EvaluationResult.objects.create(
            prompt=self.prompt,
            original_prompt="Test",
            final_prompt="Improved",
            initial_score=3.0,
            final_score=8.5,
            summary="Good improvement",
            status="ready",
            full_report={}
        )

        improvement = result.final_score - result.initial_score
        self.assertEqual(improvement, 5.5)
