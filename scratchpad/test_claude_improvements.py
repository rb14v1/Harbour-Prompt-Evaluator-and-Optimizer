"""
Test Claude as pure LLM (no dimension awareness).
Claude improves prompts naturally without knowing about 8 dimensions.
Tests all 50 samples from dataset OR accepts user prompts.
"""

import json
import os
from datetime import datetime
from anthropic import Anthropic

client = Anthropic()

def load_dataset():
    with open('dataset_50_samples.json', 'r') as f:
        return json.load(f)

# SIMPLE: Claude just improves naturally (no dimension instructions)
SIMPLE_PROMPT = """Improve this prompt to be clearer, more detailed, and more actionable:

{prompt}

Provide ONLY the improved prompt."""

def get_claude_improvement(deficient_prompt, model="claude-opus-5-5"):
    """Get Claude's improvement - pure LLM"""
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": SIMPLE_PROMPT.format(prompt=deficient_prompt)
                }
            ]
        )
        return message.content[0].text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def test_single_prompt(deficient_prompt):
    """Test a single user prompt"""
    print(f"\nUser Prompt: {deficient_prompt}")
    improved = get_claude_improvement(deficient_prompt)
    print(f"Claude Improved: {improved}")
    return improved

def test_all_50_samples():
    """Test ALL 50 samples from dataset"""
    dataset = load_dataset()
    results = []

    print(f"\n{'#'*60}")
    print(f"Testing ALL 50 prompts with Claude (Pure LLM)")
    print(f"{'#'*60}\n")

    for i, sample in enumerate(dataset, 1):
        sample_id = sample['sample_id']
        deficient = sample['original_deficient_prompt']

        print(f"[{i:2d}/50] {sample_id}: {deficient}")

        # Get Claude's improvement
        claude_improved = get_claude_improvement(deficient)

        result = {
            'sample_id': sample_id,
            'deficient_prompt': deficient,
            'claude_improved': claude_improved,
            'project_improved': sample['claude_improved_prompt'],
            'timestamp': datetime.now().isoformat()
        }

        results.append(result)

    return results

def test_user_prompts():
    """Accept prompts from user input"""
    results = []

    print(f"\n{'#'*60}")
    print("Enter your own prompts to improve (type 'done' to finish)")
    print(f"{'#'*60}\n")

    count = 1
    while True:
        user_prompt = input(f"[{count}] Enter prompt (or 'done'): ").strip()

        if user_prompt.lower() == 'done':
            break

        if not user_prompt:
            print("Empty prompt, try again.\n")
            continue

        print("Improving with Claude...")
        claude_improved = get_claude_improvement(user_prompt)

        result = {
            'sample_id': f'USER_{count}',
            'deficient_prompt': user_prompt,
            'claude_improved': claude_improved,
            'timestamp': datetime.now().isoformat()
        }

        results.append(result)

        print(f"Claude's Version:\n{claude_improved}\n")
        print("-" * 60 + "\n")

        count += 1

    return results

def save_results(results, output_file):
    """Save test results"""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

if __name__ == "__main__":
    import sys

    print("\n" + "="*60)
    print("CLAUDE IMPROVEMENTS (Pure LLM, No Dimensions)")
    print("="*60)

    if len(sys.argv) > 1 and sys.argv[1] == 'all':
        # Test all 50 samples
        results = test_all_50_samples()
        save_results(results, 'claude_test_results_all_50.json')
        print(f"\n✓ Tested {len(results)}/50 samples")

    else:
        # Test user input prompts
        results = test_user_prompts()

        if results:
            save_results(results, 'claude_test_results_user.json')
            print(f"\n✓ Tested {len(results)} user prompts")
