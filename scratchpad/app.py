"""
Flask backend for Claude Prompt Improver
Handles API calls and improvement logic
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from anthropic import Anthropic

app = Flask(__name__)

# Initialize Anthropic client with API key
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set!")
    print("Set it first: $env:ANTHROPIC_API_KEY = 'your-key'")

client = Anthropic(api_key=api_key)

# Load the 50-sample dataset
def load_dataset():
    try:
        with open('dataset_50_samples.json', 'r') as f:
            return json.load(f)
    except:
        return []

DATASET = load_dataset()

SIMPLE_PROMPT = """Improve this prompt to be clearer, more detailed, and more actionable:

{prompt}

Provide ONLY the improved prompt."""

def get_claude_improvement(deficient_prompt):
    """Get Claude's improvement - pure LLM"""
    try:
        message = client.messages.create(
            model="claude-opus-5-5",
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

@app.route('/')
def index():
    return render_template('improve.html')

@app.route('/compare')
def compare_page():
    return render_template('compare.html')

@app.route('/api/improve', methods=['POST'])
def improve_prompt():
    """API endpoint to improve a prompt"""
    data = request.json
    user_prompt = data.get('prompt', '').strip()

    if not user_prompt:
        return jsonify({'error': 'Prompt is empty'}), 400

    improved = get_claude_improvement(user_prompt)

    response = {
        'deficient_prompt': user_prompt,
        'claude_improved': improved,
        'timestamp': datetime.now().isoformat()
    }

    return jsonify(response)

@app.route('/api/compare-all', methods=['GET'])
def compare_all():
    """API endpoint to get all 50 samples with improvements"""
    results = []

    for i, sample in enumerate(DATASET):
        result = {
            'sample_id': sample['sample_id'],
            'deficient_prompt': sample['original_deficient_prompt'],
            'project_improved': sample['claude_improved_prompt'],
            'claude_improved': None
        }
        results.append(result)

    return jsonify(results)

@app.route('/api/compare-samples', methods=['POST'])
def compare_samples():
    """API endpoint to compare specific samples"""
    data = request.json
    sample_ids = data.get('sample_ids', [])

    results = []

    for sample_id in sample_ids:
        # Find sample in dataset
        sample = next((s for s in DATASET if s['sample_id'] == sample_id), None)
        if sample:
            deficient = sample['original_deficient_prompt']
            claude_improved = get_claude_improvement(deficient)

            result = {
                'sample_id': sample_id,
                'deficient_prompt': deficient,
                'project_improved': sample['claude_improved_prompt'],
                'claude_improved': claude_improved,
                'similarity': calculate_similarity(claude_improved, sample['claude_improved_prompt'])
            }
            results.append(result)

    return jsonify(results)

def calculate_similarity(text1, text2):
    """Calculate text similarity ratio (0-1)"""
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, text1.lower(), text2.lower())
    return round(matcher.ratio(), 2)

if __name__ == '__main__':
    if not api_key:
        print("\n" + "="*60)
        print("SETUP REQUIRED")
        print("="*60)
        print("\nSet ANTHROPIC_API_KEY environment variable:")
        print("\nPowerShell:")
        print("  $env:ANTHROPIC_API_KEY = 'your-api-key'")
        print("\nCmd:")
        print("  set ANTHROPIC_API_KEY=your-api-key")
        print("\nThen run this script again.")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("Starting Claude Prompt Improver")
        print("="*60)
        print("\nOpen browser: http://localhost:5000")
        print("="*60 + "\n")
        app.run(debug=True, port=5000)
