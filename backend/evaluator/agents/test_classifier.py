"""
Test suite for Classifier Agent.
Tests pattern-based and LLM-based classification.
"""

import unittest
from classifier import ClassifierAgent


class TestClassifierAgent(unittest.TestCase):
    """Test Classifier Agent functionality."""

    def setUp(self):
        """Initialize classifier for testing (LLM disabled for unit tests)."""
        self.classifier = ClassifierAgent(use_llm=False)

    def test_create_content_classification(self):
        """Test classification of 'Create Content' prompts."""
        prompts = [
            "Write a blog post about machine learning.",
            "Compose a newsletter for tech enthusiasts.",
            "Create a product description for an e-commerce site.",
            "Draft a press release announcing our Series B funding.",
            "Write social media content for our product launch.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Create Content',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.5,
                             f"Low confidence for: {prompt}")
            self.assertIn(result['complexity'], self.classifier.COMPLEXITY_LEVELS)

    def test_research_classification(self):
        """Test classification of 'Research' prompts."""
        prompts = [
            "Research AI adoption in healthcare.",
            "Find information about cloud computing trends.",
            "Look up market statistics for the SaaS industry.",
            "Investigate emerging technologies in 2024.",
            "Explore best practices for remote work.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Research',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.4)

    def test_deep_research_analysis_classification(self):
        """Test classification of 'Deep Research / Analysis' prompts."""
        prompts = [
            "Conduct a comprehensive competitive analysis of project management tools.",
            "Analyze the impact of AI regulation on tech startups.",
            "Perform an in-depth study of market trends in fintech.",
            "Evaluate the strategic implications of cloud adoption.",
            "Examine customer churn factors and retention strategies.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Deep Research / Analysis',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.4)

    def test_plan_and_organize_classification(self):
        """Test classification of 'Plan and Organize' prompts."""
        prompts = [
            "Create a 12-week project plan for building a data pipeline.",
            "Plan a hackathon with participant tiers and judging criteria.",
            "Develop a 24-month product roadmap with quarterly milestones.",
            "Create a project timeline and resource allocation plan.",
            "Schedule a series of team meetings and workshops.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Plan and Organize',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.5)

    def test_ideate_classification(self):
        """Test classification of 'Ideate' prompts."""
        prompts = [
            "Brainstorm 10 innovative startup ideas for sustainable tech.",
            "Generate business ideas for a B2B SaaS platform.",
            "Come up with creative marketing campaign concepts.",
            "Ideate new product features based on customer feedback.",
            "Create concepts for a new product line.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Ideate',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.4)

    def test_summarize_classification(self):
        """Test classification of 'Summarize' prompts."""
        prompts = [
            "Summarize this research paper in 300 words.",
            "Create an executive summary of the quarterly earnings report.",
            "Write a brief overview of the market analysis.",
            "Condense the blog post into key takeaways.",
            "Create an abstract of the study.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Summarize',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.4)

    def test_explain_classification(self):
        """Test classification of 'Explain' prompts."""
        prompts = [
            "Explain how transformer neural networks work.",
            "Clarify the difference between REST and GraphQL APIs.",
            "Teach someone how to set up a Docker container.",
            "Define microservices architecture and its benefits.",
            "Describe the machine learning model training process.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Explain',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.4)

    def test_optimize_classification(self):
        """Test classification of 'Optimize' prompts."""
        prompts = [
            "Optimize a Python database query for performance.",
            "Improve the React app's load time on mobile.",
            "Enhance the API response time and reduce bandwidth.",
            "Refactor the code for better efficiency.",
            "Speed up the data processing pipeline.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['task_type'], 'Optimize',
                           f"Failed to classify: {prompt}")
            self.assertGreater(result['confidence'], 0.4)

    def test_simple_complexity(self):
        """Test detection of 'Simple' complexity level."""
        prompts = [
            "Write a blog post.",
            "Create code.",
            "Summarize text.",
            "Explain AI.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['complexity'], 'Simple',
                           f"Failed to classify as Simple: {prompt}")

    def test_moderate_complexity(self):
        """Test detection of 'Moderate' complexity level."""
        prompts = [
            "Write a technical blog post about machine learning for engineers.",
            "Create a REST API endpoint with JWT authentication.",
            "Summarize a research paper highlighting key findings.",
            "Explain blockchain technology to business executives.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['complexity'], 'Moderate',
                           f"Failed to classify as Moderate: {prompt}")

    def test_complex_complexity(self):
        """Test detection of 'Complex' complexity level."""
        prompts = [
            "Build a distributed machine learning pipeline with data preprocessing, model training, evaluation, and deployment across multiple servers.",
            "Create a comprehensive microservices architecture with Kubernetes orchestration, monitoring, and auto-scaling policies.",
            "Conduct a strategic analysis of AI regulation impact on tech startups including market consolidation forecasts.",
            "Plan a 24-month product roadmap with quarterly milestones, feature prioritization, resource allocation, and risk management.",
        ]

        for prompt in prompts:
            result = self.classifier.classify(prompt)
            self.assertEqual(result['complexity'], 'Complex',
                           f"Failed to classify as Complex: {prompt}")

    def test_confidence_scores(self):
        """Test confidence score calculation."""
        # Clear classification should have high confidence
        clear_prompt = "Write Python code to sort an array."
        clear_result = self.classifier.classify(clear_prompt)
        self.assertGreater(clear_result['confidence'], 0.6)

        # Ambiguous classification should have lower confidence
        ambiguous_prompt = "Do something about data."
        ambiguous_result = self.classifier.classify(ambiguous_prompt)
        self.assertLess(ambiguous_result['confidence'], 0.7)

    def test_output_structure(self):
        """Test that output has correct structure."""
        prompt = "Write a blog post about artificial intelligence."
        result = self.classifier.classify(prompt)

        # Check all required fields exist
        required_fields = ['task_type', 'complexity', 'confidence', 'reasoning', 'classification_method']
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")

        # Check field types
        self.assertIsInstance(result['task_type'], str)
        self.assertIsInstance(result['complexity'], str)
        self.assertIsInstance(result['confidence'], (int, float))
        self.assertIsInstance(result['reasoning'], str)
        self.assertIsInstance(result['classification_method'], str)

        # Check value ranges
        self.assertIn(result['task_type'], self.classifier.TASK_CATEGORIES)
        self.assertIn(result['complexity'], self.classifier.COMPLEXITY_LEVELS)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        self.assertIn(result['classification_method'], ['pattern_based', 'llm_verified', 'error'])

    def test_category_info(self):
        """Test category info retrieval."""
        info = self.classifier.get_category_info("Create Content")

        self.assertEqual(info['category'], "Create Content")
        self.assertIsInstance(info['keywords'], list)
        self.assertGreater(len(info['keywords']), 0)
        self.assertIn('write', info['keywords'])
        self.assertIn('article', info['keywords'])

    def test_all_categories_accessible(self):
        """Test that all categories can be accessed."""
        for category in self.classifier.TASK_CATEGORIES:
            info = self.classifier.get_category_info(category)
            self.assertEqual(info['category'], category)
            self.assertGreater(len(info['keywords']), 0)

    def test_mixed_category_prompts(self):
        """Test prompts that might match multiple categories."""
        # Should classify as Create Content, not Optimize / Improve
        prompt1 = "Write a guide about best practices for database optimization."
        result1 = self.classifier.classify(prompt1)
        self.assertEqual(result1['task_type'], 'Create Content')

        # Should classify as Deep Research / Analysis, not Research
        prompt2 = "Conduct detailed analysis and research on market trends."
        result2 = self.classifier.classify(prompt2)
        self.assertEqual(result2['task_type'], 'Deep Research / Analysis')

    def test_error_handling(self):
        """Test error handling for edge cases."""
        # Empty prompt
        result = self.classifier.classify("")
        self.assertIn(result['task_type'], self.classifier.TASK_CATEGORIES + ['Unknown'])
        self.assertGreaterEqual(result['confidence'], 0.0)

        # Very long prompt
        long_prompt = "Write " * 500 + "a blog post about AI"
        result = self.classifier.classify(long_prompt)
        self.assertIn(result['task_type'], self.classifier.TASK_CATEGORIES + ['Unknown'])

        # Special characters
        special_prompt = "Write!!! @@@code###for$$$AI***optimization"
        result = self.classifier.classify(special_prompt)
        self.assertIn(result['task_type'], self.classifier.TASK_CATEGORIES + ['Unknown'])


class TestClassifierAgentMetrics(unittest.TestCase):
    """Test metrics and performance of Classifier Agent."""

    def setUp(self):
        self.classifier = ClassifierAgent(use_llm=False)

    def test_classification_accuracy_across_categories(self):
        """Test overall classification accuracy."""
        test_cases = [
            # (prompt, expected_category)
            ("Write a blog post", "Create Content"),
            ("Research the market", "Research"),
            ("Analyze competitors", "Deep Research / Analysis"),
            ("Plan a project", "Plan and Organize"),
            ("Brainstorm ideas", "Ideate / Brainstorm"),
            ("Summarize the report", "Summarize / Review"),
            ("Explain AI", "Explain / Teach"),
            ("Optimize performance", "Optimize / Improve"),
        ]

        correct = 0
        for prompt, expected_category in test_cases:
            result = self.classifier.classify(prompt)
            if result['task_type'] == expected_category:
                correct += 1

        accuracy = correct / len(test_cases)
        self.assertGreater(accuracy, 0.7, f"Classification accuracy too low: {accuracy}")

    def test_confidence_consistency(self):
        """Test that similar prompts have similar confidence scores."""
        similar_prompts = [
            "Write a blog post about AI",
            "Create a blog post about machine learning",
            "Compose a blog post on artificial intelligence",
        ]

        results = [self.classifier.classify(p) for p in similar_prompts]
        confidences = [r['confidence'] for r in results]

        # All should be classified as Create Content
        for result in results:
            self.assertEqual(result['task_type'], 'Create Content')

        # Confidences should be relatively similar (within 0.3)
        min_conf = min(confidences)
        max_conf = max(confidences)
        confidence_spread = max_conf - min_conf
        self.assertLess(confidence_spread, 0.3,
                       f"Confidences too spread: {confidences}")


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
