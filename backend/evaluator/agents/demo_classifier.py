"""
Quick demo of Classifier Agent functionality.
Run without external dependencies to verify implementation.
"""

from classifier import ClassifierAgent


def demo_classification():
    """Demonstrate classifier on various prompts."""
    print("="*80)
    print("CLASSIFIER AGENT DEMO - WITH DATASET-DRIVEN CLASSIFICATION")
    print("="*80)

    # Initialize classifier with dataset for improved accuracy
    classifier = ClassifierAgent(use_llm=False, use_dataset=True)
    print(f"\n[INFO] Dataset-driven classification: {classifier.use_dataset}")
    print(f"[INFO] Dataset examples loaded: {len(classifier.dataset_examples)} categories")

    # Test prompts across all categories
    test_prompts = {
        "Create Content": [
            "Write a blog post about AI",
            "Create a product description for SaaS tool",
            "Compose a newsletter for tech professionals"
        ],
        "Create Code": [
            "Write a Python function to validate emails",
            "Build a REST API endpoint with authentication",
            "Create a React component for todo list"
        ],
        "Research": [
            "Research AI adoption in healthcare",
            "Find information about cloud computing",
            "Look up market statistics for SaaS"
        ],
        "Deep Research / Analysis": [
            "Conduct competitive analysis of project management tools",
            "Analyze AI regulation impact on startups",
            "Perform in-depth study of fintech trends"
        ],
        "Plan and Organize": [
            "Create a 12-week project plan",
            "Plan a hackathon with judging criteria",
            "Develop a 24-month product roadmap"
        ],
        "Ideate": [
            "Brainstorm startup ideas for sustainable tech",
            "Generate business ideas for B2B SaaS",
            "Come up with creative marketing concepts"
        ],
        "Summarize": [
            "Summarize research paper in key findings",
            "Create executive summary of earnings",
            "Write brief overview of market analysis"
        ],
        "Explain": [
            "Explain transformer neural networks",
            "Clarify REST vs GraphQL APIs",
            "Teach Docker container setup"
        ],
        "Optimize": [
            "Optimize Python database queries",
            "Improve React app load time",
            "Enhance API response time"
        ]
    }

    total_tests = 0
    correct_classifications = 0

    # Test each category
    for expected_category, prompts in test_prompts.items():
        print(f"\n{'─'*80}")
        print(f"Testing: {expected_category}")
        print(f"{'─'*80}")

        for prompt in prompts:
            total_tests += 1
            result = classifier.classify(prompt)

            # Check if classification is correct
            is_correct = result['task_type'] == expected_category
            if is_correct:
                correct_classifications += 1
                status = "✓ PASS"
            else:
                status = "✗ FAIL"

            # Display result
            print(f"\n{status}")
            print(f"  Prompt: {prompt}")
            print(f"  Expected: {expected_category}")
            print(f"  Got: {result['task_type']}")
            print(f"  Complexity: {result['complexity']}")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Method: {result['classification_method']}")
            print(f"  Reasoning: {result['reasoning'][:80]}...")

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    accuracy = (correct_classifications / total_tests) * 100 if total_tests > 0 else 0
    print(f"Total Tests: {total_tests}")
    print(f"Correct: {correct_classifications}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"\n{'Status: ' + ('✓ PASS' if accuracy >= 70 else '✗ FAIL')}")
    print("="*80)

    return correct_classifications, total_tests


def demo_complexity_detection():
    """Demonstrate complexity detection."""
    print("\n\n" + "="*80)
    print("COMPLEXITY DETECTION DEMO")
    print("="*80)

    classifier = ClassifierAgent(use_llm=False)

    complexity_examples = {
        "Simple": [
            "Write a blog post",
            "Create code",
            "Summarize text"
        ],
        "Moderate": [
            "Write a technical blog on ML for engineers (1500 words, include examples)",
            "Build REST API with JWT authentication and error handling",
            "Summarize research paper highlighting key findings and implications"
        ],
        "Complex": [
            "Build distributed ML pipeline with preprocessing, training, evaluation, deployment, monitoring, and A/B testing across multiple servers",
            "Plan 24-month product roadmap with quarterly phases, resource allocation, dependencies, risks, and competitive analysis",
            "Conduct comprehensive strategic analysis with market sizing, competitive positioning, financial projections, and 5-year forecasts"
        ]
    }

    for expected_complexity, prompts in complexity_examples.items():
        print(f"\n{'─'*80}")
        print(f"Expected Complexity: {expected_complexity}")
        print(f"{'─'*80}")

        for prompt in prompts:
            result = classifier.classify(prompt)
            is_correct = result['complexity'] == expected_complexity
            status = "✓" if is_correct else "✗"

            print(f"\n{status} Prompt: {prompt[:60]}...")
            print(f"   Expected: {expected_complexity}")
            print(f"   Got: {result['complexity']}")

    print("\n" + "="*80)


def demo_category_keywords():
    """Show keywords for each category."""
    print("\n\n" + "="*80)
    print("CATEGORY KEYWORDS")
    print("="*80)

    classifier = ClassifierAgent(use_llm=False)

    for category in classifier.TASK_CATEGORIES:
        info = classifier.get_category_info(category)
        keywords = info['keywords']

        print(f"\n{category} ({len(keywords)} keywords):")
        print(f"  {', '.join(keywords[:10])}")
        if len(keywords) > 10:
            print(f"  ... and {len(keywords) - 10} more")

    print("\n" + "="*80)


def demo_edge_cases():
    """Test edge cases."""
    print("\n\n" + "="*80)
    print("EDGE CASES DEMO")
    print("="*80)

    classifier = ClassifierAgent(use_llm=False)

    edge_cases = [
        ("", "Empty prompt"),
        ("?", "Single character"),
        ("Do something about data", "Very vague"),
        ("Write" * 100 + " code", "Very long with repetition"),
        ("!!!@@@###$$$%%%&&&", "Only special characters"),
        ("123 456 789 000 111 222", "Only numbers"),
    ]

    print("\nTesting edge cases:\n")
    for prompt, description in edge_cases:
        result = classifier.classify(prompt)
        print(f"{description}:")
        print(f"  Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"  Prompt: {prompt}")
        print(f"  Classification: {result['task_type']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print()

    print("="*80)


def demo_accuracy_comparison():
    """Compare classifier accuracy with and without dataset."""
    print("\n\n" + "="*80)
    print("ACCURACY COMPARISON: WITH vs WITHOUT DATASET")
    print("="*80)

    test_prompts = {
        "Create Content": [
            "Write a blog post about AI",
            "Create a product description",
            "Compose a newsletter"
        ],
        "Create Code": [
            "Write a Python function",
            "Build a REST API",
            "Create a React component"
        ],
        "Research": [
            "Research market trends",
            "Find information about cloud",
            "Look up statistics"
        ],
        "Deep Research / Analysis": [
            "Conduct competitive analysis",
            "Analyze AI regulation impact",
            "Perform in-depth study"
        ],
        "Plan and Organize": [
            "Create project plan",
            "Plan a hackathon",
            "Develop roadmap"
        ],
        "Ideate": [
            "Brainstorm startup ideas",
            "Generate business ideas",
            "Come up with concepts"
        ],
        "Summarize": [
            "Summarize research paper",
            "Create executive summary",
            "Write overview"
        ],
        "Explain": [
            "Explain neural networks",
            "Clarify APIs",
            "Teach Docker"
        ],
        "Optimize": [
            "Optimize queries",
            "Improve load time",
            "Enhance performance"
        ]
    }

    # Test WITHOUT dataset
    classifier_no_dataset = ClassifierAgent(use_llm=False, use_dataset=False)
    correct_no_dataset = 0
    total_no_dataset = 0

    print("\n[TEST 1] WITHOUT Dataset:")
    for expected_category, prompts in test_prompts.items():
        for prompt in prompts:
            result = classifier_no_dataset.classify(prompt)
            if result['task_type'] == expected_category:
                correct_no_dataset += 1
            total_no_dataset += 1

    accuracy_no_dataset = (correct_no_dataset / total_no_dataset) * 100

    # Test WITH dataset
    classifier_with_dataset = ClassifierAgent(use_llm=False, use_dataset=True)
    correct_with_dataset = 0
    total_with_dataset = 0

    print(f"Accuracy WITHOUT dataset: {correct_no_dataset}/{total_no_dataset} = {accuracy_no_dataset:.1f}%")

    print("\n[TEST 2] WITH Dataset:")
    for expected_category, prompts in test_prompts.items():
        for prompt in prompts:
            result = classifier_with_dataset.classify(prompt)
            if result['task_type'] == expected_category:
                correct_with_dataset += 1
            total_with_dataset += 1

    accuracy_with_dataset = (correct_with_dataset / total_with_dataset) * 100

    print(f"Accuracy WITH dataset: {correct_with_dataset}/{total_with_dataset} = {accuracy_with_dataset:.1f}%")

    improvement = accuracy_with_dataset - accuracy_no_dataset
    print("\n" + "─"*80)
    print(f"Improvement: {improvement:+.1f}%")
    print(f"Status: {'✅ PASS (>80%)' if accuracy_with_dataset > 80 else '⚠️  Continue improving'}")
    print("="*80)

    return accuracy_with_dataset


if __name__ == '__main__':
    print("\n")

    # Run demos
    correct, total = demo_classification()
    demo_complexity_detection()
    demo_category_keywords()
    demo_edge_cases()
    final_accuracy = demo_accuracy_comparison()

    print("\n" + "="*80)
    print("DEMO COMPLETE - ENHANCED CLASSIFIER")
    print("="*80)
    print(f"\nFinal Classification Accuracy: {final_accuracy:.1f}%")
    print("\nKey Features Demonstrated:")
    print("  ✓ Dataset-driven classification (9 categories)")
    print("  ✓ Dynamic keyword extraction from dataset")
    print("  ✓ Similarity-based matching with examples")
    print("  ✓ Complexity detection (Simple/Moderate/Complex)")
    print("  ✓ Confidence scoring with improved algorithm")
    print("  ✓ Reasoning generation")
    print("  ✓ Category keyword lookup")
    print("  ✓ Edge case handling")
    print("\nEnhancements from Dataset Integration:")
    print("  ✓ 40% keyword matching + 60% similarity scoring")
    print("  ✓ Dynamic keyword extraction from 270 dataset examples")
    print("  ✓ Improved confidence calculation")
    print("  ✓ Better handling of ambiguous prompts")
    print("\n" + "="*80)
