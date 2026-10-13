"""
Compare Claude-generated improvements with your project's improvements.
Shows side-by-side comparison without dimension analysis.
"""

import json
from difflib import SequenceMatcher
from datetime import datetime

def calculate_similarity(text1, text2):
    """Calculate text similarity ratio (0-1)"""
    matcher = SequenceMatcher(None, text1.lower(), text2.lower())
    return matcher.ratio()

def compare_improvements(test_file='claude_test_results_all_50.json'):
    """Compare Claude vs Project improvements"""

    try:
        with open(test_file, 'r') as f:
            test_results = json.load(f)
    except FileNotFoundError:
        print(f"Error: {test_file} not found")
        print("Run: python test_claude_improvements.py all")
        return

    comparisons = []

    print(f"\n{'='*80}")
    print("COMPARISON: Claude Improvements vs Your Project Improvements")
    print(f"{'='*80}\n")

    for i, result in enumerate(test_results, 1):
        sample_id = result['sample_id']
        deficient = result['deficient_prompt']
        claude = result['claude_improved']
        project = result.get('project_improved', '')

        # Calculate similarity
        similarity = calculate_similarity(claude, project) if project else 0

        comparison = {
            'sample_id': sample_id,
            'deficient_prompt': deficient,
            'claude_improved': claude,
            'project_improved': project,
            'similarity': similarity,
            'length_claude': len(claude),
            'length_project': len(project) if project else 0
        }

        comparisons.append(comparison)

        # Print sample comparison
        print(f"[{i}] {sample_id}")
        print(f"Deficient: {deficient}")
        print(f"\nCLAUDE ({len(claude)} chars):")
        print(f"  {claude[:150]}..." if len(claude) > 150 else f"  {claude}")

        if project:
            print(f"\nYOUR PROJECT ({len(project)} chars):")
            print(f"  {project[:150]}..." if len(project) > 150 else f"  {project}")
            print(f"\nSimilarity: {similarity:.1%}")

        print(f"\n{'-'*80}\n")

    # Save full comparison
    report = {
        'total_samples': len(comparisons),
        'timestamp': datetime.now().isoformat(),
        'comparisons': comparisons
    }

    with open('comparison_results.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Full comparison saved to: comparison_results.json")

if __name__ == "__main__":
    import sys

    test_file = sys.argv[1] if len(sys.argv) > 1 else 'claude_test_results_all_50.json'
    compare_improvements(test_file)
