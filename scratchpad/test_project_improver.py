"""
Test your project's Improver agent against Claude improvements.
Compares results from your actual pipeline with Claude-generated improvements.

HOW TO USE:
1. Update PROJECT_PATH below to your actual project directory
2. Make sure your project modules are importable
3. Run: python test_project_improver.py
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION - UPDATE THESE PATHS
# ============================================================================

# Path to your project root
PROJECT_PATH = r"c:\Users\admin\Downloads\project\prompt-evaluator-and-optimizer"

# Module paths to import your agents (adjust based on your project structure)
# Example: backend/evaluator/agents/improver.py
IMPROVER_MODULE = "backend.evaluator.agents"  # Adjust this path
VALIDATOR_MODULE = "backend.evaluator.agents"  # Adjust this path

# ============================================================================

def setup_project_path():
    """Add project to Python path so we can import its modules"""
    sys.path.insert(0, PROJECT_PATH)
    print(f"✓ Added to path: {PROJECT_PATH}")

def load_test_dataset(num_samples=5):
    """Load test samples from our generated dataset"""
    dataset_file = "dataset_50_samples.json"

    if not os.path.exists(dataset_file):
        print(f"Error: {dataset_file} not found")
        return []

    with open(dataset_file, 'r') as f:
        data = json.load(f)

    return data[:num_samples]

def test_project_improver_on_prompt(deficient_prompt):
    """
    Run your project's Improver agent on a deficient prompt.

    This is a TEMPLATE - you need to adjust based on your actual project structure.
    """

    try:
        # ADJUST THIS IMPORT based on your actual project structure
        # Example imports (these are placeholders):

        # Option 1: If you have an Improver class
        # from backend.evaluator.agents.improver import ImproverAgent
        # improver = ImproverAgent()
        # result = improver.improve(deficient_prompt)

        # Option 2: If you have a pipeline function
        # from backend.evaluator.pipeline import run_improvement
        # result = run_improvement(deficient_prompt)

        # Option 3: If you have individual agents
        # from backend.evaluator.agents import Validator, Improver
        # validator = Validator()
        # improver = Improver()
        # analysis = validator.validate(deficient_prompt)
        # result = improver.improve(deficient_prompt, analysis)

        # PLACEHOLDER: Return a mock response for demonstration
        result = {
            'improved_prompt': f"IMPROVED VERSION: {deficient_prompt}",
            'status': 'success',
            'note': 'This is a placeholder. Update the import statements above.'
        }

        return result

    except ImportError as e:
        return {
            'improved_prompt': None,
            'status': 'error',
            'error': f"Import error: {str(e)}",
            'note': 'Update IMPROVER_MODULE and VALIDATOR_MODULE paths above'
        }
    except Exception as e:
        return {
            'improved_prompt': None,
            'status': 'error',
            'error': str(e)
        }

def run_comparison_test(num_samples=5):
    """Run your Improver on test samples and compare with Claude"""

    setup_project_path()

    # Load test samples
    samples = load_test_dataset(num_samples)

    if not samples:
        print("No samples to test")
        return

    results = []

    print(f"\n{'='*60}")
    print(f"Testing Your Project's Improver Agent")
    print(f"{'='*60}")
    print(f"Samples to test: {len(samples)}\n")

    for i, sample in enumerate(samples, 1):
        deficient = sample['original_deficient_prompt']
        claude_version = sample['claude_improved_prompt']

        print(f"[{i}/{len(samples)}] Testing: {deficient[:40]}...")

        # Run your project's improver
        your_result = test_project_improver_on_prompt(deficient)

        result = {
            'sample_id': sample['sample_id'],
            'deficient_prompt': deficient,
            'claude_improved': claude_version,
            'your_improved': your_result.get('improved_prompt'),
            'status': your_result.get('status'),
            'error': your_result.get('error'),
            'timestamp': datetime.now().isoformat()
        }

        results.append(result)

        if your_result['status'] == 'success':
            print(f"  ✓ Generated improvement")
        else:
            print(f"  ⚠ Error: {your_result.get('error', 'Unknown error')}")

    return results

def save_results(results, output_file='project_improver_test_results.json'):
    """Save test results to file"""

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

    # Print summary
    successful = [r for r in results if r['status'] == 'success']
    errors = [r for r in results if r['status'] == 'error']

    print(f"\nSummary:")
    print(f"  Successful: {len(successful)}")
    print(f"  Errors:     {len(errors)}")

if __name__ == "__main__":
    print("="*60)
    print("PROJECT IMPROVER TEST")
    print("="*60)
    print("\nNOTE: Update the import statements in test_project_improver()")
    print("      to match your actual project structure.")
    print("\nSearching for your project modules...\n")

    # Check if project path exists
    if not os.path.exists(PROJECT_PATH):
        print(f"⚠ Project path not found: {PROJECT_PATH}")
        print("  Update PROJECT_PATH variable above.")
    else:
        print(f"✓ Project found: {PROJECT_PATH}")

        # Run tests
        results = run_comparison_test(num_samples=3)

        if results:
            save_results(results)
