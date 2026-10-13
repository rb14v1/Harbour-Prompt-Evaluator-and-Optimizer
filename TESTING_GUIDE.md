# Testing Guide: How to Check Preprocessor Agent Outputs

## Overview

This guide shows you how to test the Preprocessor Agent and view evaluation outputs using two approaches:
1. **Preprocessor in Isolation** - Test just the text normalization
2. **Full Pipeline** - Send a prompt and get complete evaluation with all agent outputs

---

## APPROACH 1: Preprocessor Agent in Isolation

### Method A: Via Python Script

**Step 1:** Create a test script

```bash
cd C:\Users\admin\prompt-evaluator-and-optimizer\backend
```

**Step 2:** Create file `test_preprocessor.py`

```python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from evaluator.agents.preprocessor import PreprocessorAgent
import json

# Initialize agent
agent = PreprocessorAgent()

# Test prompts with various whitespace issues
test_prompts = [
    "Write   a   Python   function   that   sorts   arrays",
    "  Create a REST API endpoint with proper error handling  ",
    "Design   a   database    schema\n\nfor   a   blog   app",
    "Refactor this code\n  \n\nto   use   async/await",
]

print("=" * 80)
print("PREPROCESSOR AGENT - ISOLATION TESTING")
print("=" * 80)

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n{'─' * 80}")
    print(f"TEST {i}")
    print(f"{'─' * 80}")
    
    # Show original
    print(f"\nINPUT PROMPT (raw):")
    print(f"  {repr(prompt)}")
    
    # Process
    result = agent.process(prompt)
    
    # Show output
    print(f"\nOUTPUT FROM PREPROCESSOR:")
    print(f"  prompt_id:       {result['prompt_id']}")
    print(f"  original_prompt: {repr(result['original_prompt'])}")
    print(f"  processed_prompt: {repr(result['processed_prompt'])}")
    print(f"  metadata:")
    print(f"    - length: {result['metadata']['length']} words")
    print(f"    - timestamp: {result['metadata']['timestamp']}")
    print(f"    - version: {result['metadata']['version']}")

print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80)
```

**Step 3:** Run the script

```bash
# Activate virtual environment (if not already active)
..\venv\Scripts\Activate.ps1

# Run test
python test_preprocessor.py
```

**Expected Output:**

```
════════════════════════════════════════════════════════════════════════════════
PREPROCESSOR AGENT - ISOLATION TESTING
════════════════════════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────────────────────────
TEST 1
────────────────────────────────────────────────────────────────────────────────

INPUT PROMPT (raw):
  'Write   a   Python   function   that   sorts   arrays'

OUTPUT FROM PREPROCESSOR:
  prompt_id:       a1b2c3d4-e5f6-7890-abcd-ef1234567890
  original_prompt: 'Write   a   Python   function   that   sorts   arrays'
  processed_prompt: 'Write a Python function that sorts arrays'
  metadata:
    - length: 7 words
    - timestamp: 2026-09-10T15:30:45.123456
    - version: 1
```

**What This Shows:**
- ✓ Original prompt preserved exactly as input
- ✓ Extra whitespace removed
- ✓ Word count calculated
- ✓ Unique ID generated
- ✓ Timestamp recorded

---

### Method B: Via Django Shell

**Step 1:** Start Django shell

```bash
cd backend
python manage.py shell
```

**Step 2:** Import and test

```python
from evaluator.agents.preprocessor import PreprocessorAgent
import json

agent = PreprocessorAgent()

# Test a prompt
prompt = "Write   a   Python   function"
result = agent.process(prompt)

# Pretty print
print(json.dumps(result, indent=2))
```

**Step 3:** Exit

```python
exit()
```

---

## APPROACH 2: Full Pipeline with curl

This shows how the Preprocessor output feeds into the full evaluation pipeline.

### Method A: Basic curl Command

**Step 1:** Ensure server is running

```bash
cd backend
python manage.py runserver
```

Server should show: `Starting development server at http://127.0.0.1:8000/`

**Step 2:** Open a NEW terminal and run curl

#### Test 1: Simple Prompt

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a function that sorts arrays"}'
```

#### Test 2: With Extra Whitespace (shows preprocessing)

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write   a   function   that   sorts   arrays"}'
```

#### Test 3: Complex Prompt

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Python REST API that handles CRUD operations for a blog app with proper error handling, validation, and documentation"}'
```

### Method B: Pretty-Printed Output (Using Python to format)

**Step 1:** Create `test_api.py`

```python
import requests
import json

# Test prompts
test_prompts = [
    "Write a function that sorts arrays",
    "Create  a  REST  API  endpoint",
    "Design a comprehensive database schema for an e-commerce platform with products, users, and orders"
]

print("=" * 80)
print("FULL PIPELINE EVALUATION - VIA API")
print("=" * 80)

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n{'─' * 80}")
    print(f"TEST {i}: {prompt[:50]}...")
    print(f"{'─' * 80}")
    
    try:
        # Send to API
        response = requests.post(
            'http://localhost:8000/api/evaluations/evaluate/',
            json={"prompt": prompt},
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            
            # Show key outputs from each agent
            print("\n1. PREPROCESSOR OUTPUT:")
            print(f"   - Original: {repr(result['original_prompt'][:60])}...")
            print(f"   - Processed: {repr(result['final_prompt'][:60])}...")
            print(f"   - Prompt ID: {result['prompt_id']}")
            
            print("\n2. CLASSIFIER OUTPUT:")
            print(f"   - Task Type: {result['classification']['task_type']}")
            print(f"   - Complexity: {result['classification']['complexity']}")
            print(f"   - Confidence: {result['classification']['confidence']:.2%}")
            
            print("\n3. ANALYZER OUTPUT:")
            print(f"   - Intent: {result['analysis']['intent']}")
            print(f"   - Requirements: {len(result['analysis']['requirements'])} items")
            print(f"   - Missing Info: {len(result['analysis']['missing_information'])} items")
            
            print("\n4. VALIDATOR OUTPUT (8 Dimensions):")
            dim_scores = result['initial_evaluation']['dimension_scores']
            for dim, score in dim_scores.items():
                print(f"   - {dim.capitalize()}: {score}/10.0")
            
            print("\n5. SCORING ENGINE OUTPUT:")
            print(f"   - Overall Score: {result['final_score']}/10.0")
            print(f"   - Threshold: {result['initial_evaluation']['overall_issues']}")
            print(f"   - Status: {result['status']}")
            
            if result['improvements_made'] > 0:
                print("\n6. IMPROVEMENT RESULTS:")
                print(f"   - Iterations: {result['iterations_required']}")
                print(f"   - Improvements Made: {result['improvements_made']}")
                print(f"   - Final Status: {result['status']}")
                print(f"   - Summary: {result['summary']}")
            else:
                print("\n6. NO IMPROVEMENTS NEEDED:")
                print(f"   - Score already meets threshold (≥7.0)")
                
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("Make sure server is running: python manage.py runserver")

print("\n" + "=" * 80)
```

**Step 2:** Run it

```bash
# Make sure you're in the main project directory
python test_api.py
```

---

## Understanding the Output Structure

### Preprocessor Output (within full pipeline)

```json
{
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_prompt": "Write a function that sorts arrays",
  "classification": {...},
  "analysis": {...},
  "initial_evaluation": {...},
  "improvement_history": [...],
  "final_evaluation": {...},
  "final_prompt": "Write a function that sorts arrays",
  "summary": "Prompt is clear and actionable...",
  "status": "Ready",
  "improvements_made": 0,
  "iterations_required": 0,
  "timestamp": "2026-09-10T15:30:45.123456Z"
}
```

### Key Fields Explained

| Field | From Agent | Meaning |
|-------|-----------|---------|
| `prompt_id` | Preprocessor | Unique ID generated for tracking |
| `original_prompt` | Preprocessor | Your exact input (unmodified) |
| `processed_prompt` | Preprocessor | Normalized version (whitespace cleaned) |
| `final_prompt` | Report | Best version (improved or original) |
| `classification` | Classifier | Task type and complexity |
| `analysis` | Analyzer | Intent, requirements, context, etc. |
| `initial_evaluation` | Validator | Initial dimension scores |
| `improvement_history` | Improver | List of improvements (if any) |
| `final_evaluation` | Scoring | Final scores after improvements |
| `status` | Report | "Ready" or "Needs Manual Review" |

---

## Checking Results in Database

### Method A: Django Admin

**Step 1:** Go to admin panel

```
http://localhost:8000/admin
Username: admin
Password: admin123
```

**Step 2:** Navigate to Evaluator models
- Click "Prompts" to see all submitted prompts
- Click on a prompt to see details
- View Classification, Analysis, Evaluation, etc.

### Method B: Django Shell

```bash
cd backend
python manage.py shell
```

```python
from evaluator.models import EvaluationResult, Prompt

# Get all results
results = EvaluationResult.objects.all()
print(f"Total evaluations: {results.count()}")

# Get latest result
latest = results.latest('created_at')
print(f"\nLatest prompt: {latest.original_prompt}")
print(f"Original score: {latest.initial_score}")
print(f"Final score: {latest.final_score}")
print(f"Improvements: {latest.improvements_made}")

# View the full report
import json
print("\nFull Report:")
print(json.dumps(latest.full_report, indent=2))

# Get the prompt details
prompt = latest.prompt
print(f"\nPrompt ID: {prompt.id}")
print(f"Original: {prompt.original_prompt}")
print(f"Processed: {prompt.processed_prompt}")

# Get classification
if hasattr(prompt, 'classification'):
    clf = prompt.classification
    print(f"\nTask Type: {clf.task_type}")
    print(f"Complexity: {clf.complexity}")
    print(f"Confidence: {clf.confidence}")
```

---

## Example Outputs

### Example 1: Simple Prompt (No Improvement Needed)

**Input:**
```json
{"prompt": "Write a Python function that accepts a list of integers and returns the sum of all even numbers using list comprehension"}
```

**Preprocessor Contribution:**
```json
{
  "prompt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "original_prompt": "Write a Python function that accepts a list of integers and returns the sum of all even numbers using list comprehension",
  "processed_prompt": "Write a Python function that accepts a list of integers and returns the sum of all even numbers using list comprehension",
  "metadata": {
    "length": 19,
    "timestamp": "2026-09-10T15:30:45.123456Z",
    "version": 1
  }
}
```

**Final Result:**
```json
{
  "prompt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "original_prompt": "Write a Python function that accepts a list of integers and returns the sum of all even numbers using list comprehension",
  "classification": {
    "task_type": "Create Code",
    "complexity": "Moderate",
    "confidence": 0.95,
    "reasoning": "Clear request to write Python code with specific requirements"
  },
  "analysis": {
    "intent": "Write a Python function to sum even numbers from a list",
    "requirements": [
      "Accept list of integers",
      "Return sum of even numbers",
      "Use list comprehension"
    ],
    "context": [],
    "constraints": [],
    "expected_output": "Python function",
    "missing_information": [],
    "ambiguities": []
  },
  "initial_evaluation": {
    "dimension_scores": {
      "clarity": 10.0,
      "specificity": 10.0,
      "context": 7.5,
      "completeness": 10.0,
      "requirements": 10.0,
      "constraints": 7.5,
      "expected_output": 10.0,
      "actionability": 10.0
    },
    "overall_score": 9.31,
    "status": "Ready",
    "low_scoring_dimensions": [],
    "high_performing_dimensions": ["clarity", "specificity", "completeness", "requirements", "expected_output", "actionability"]
  },
  "improvement_history": [],
  "final_evaluation": {
    "dimension_scores": {
      "clarity": 10.0,
      "specificity": 10.0,
      "context": 7.5,
      "completeness": 10.0,
      "requirements": 10.0,
      "constraints": 7.5,
      "expected_output": 10.0,
      "actionability": 10.0
    },
    "overall_score": 9.31,
    "status": "Ready"
  },
  "final_prompt": "Write a Python function that accepts a list of integers and returns the sum of all even numbers using list comprehension",
  "summary": "Excellent prompt. Clear purpose, specific requirements, all parameters defined, expected output explicit. Ready for immediate execution.",
  "status": "Ready",
  "improvements_made": 0,
  "iterations_required": 0,
  "timestamp": "2026-09-10T15:30:45.123456Z"
}
```

### Example 2: Vague Prompt (Needs Improvement)

**Input:**
```json
{"prompt": "Create a function"}
```

**Preprocessor Contribution:**
```json
{
  "prompt_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "original_prompt": "Create a function",
  "processed_prompt": "Create a function",
  "metadata": {
    "length": 3,
    "timestamp": "2026-09-10T15:35:20.456789Z",
    "version": 1
  }
}
```

**Initial Evaluation (too vague):**
```json
{
  "overall_score": 2.5,
  "status": "Needs Improvement",
  "low_scoring_dimensions": ["specificity", "requirements", "constraints", "expected_output", "actionability"]
}
```

**After Improvement (Iteration 1):**
```json
{
  "improved_prompt": "Create a Python function named 'calculate_average' that takes a list of numbers as input and returns the arithmetic mean. The function should handle empty lists by returning 0, and include a docstring explaining parameters and return type.",
  "changes_made": [
    "Added language specification (Python)",
    "Specified function name and purpose",
    "Defined input type and format",
    "Specified output format (arithmetic mean)",
    "Added edge case handling (empty lists)",
    "Requested documentation"
  ],
  "dimensions_addressed": ["specificity", "requirements", "expected_output", "actionability"],
  "intent_preserved": true,
  "iteration": 1
}
```

**Final Result:**
```json
{
  "initial_evaluation": {
    "overall_score": 2.5,
    "status": "Needs Improvement"
  },
  "improvement_history": [
    {
      "iteration": 1,
      "improved_prompt": "Create a Python function named 'calculate_average' that takes a list of numbers as input and returns the arithmetic mean. The function should handle empty lists by returning 0, and include a docstring explaining parameters and return type.",
      "changes_made": [...],
      "evaluation": {
        "overall_score": 8.75
      }
    }
  ],
  "final_evaluation": {
    "overall_score": 8.75,
    "status": "Ready"
  },
  "final_prompt": "Create a Python function named 'calculate_average' that takes a list of numbers as input and returns the arithmetic mean. The function should handle empty lists by returning 0, and include a docstring explaining parameters and return type.",
  "summary": "Prompt significantly improved. Added language, function name, parameters, output format, and edge case handling. Original intent preserved.",
  "status": "Ready",
  "improvements_made": 1,
  "iterations_required": 1
}
```

---

## Troubleshooting

### Issue 1: "Connection refused" or "Cannot connect to server"

**Solution:**
```bash
# Make sure server is running in another terminal
cd backend
python manage.py runserver

# If port 8000 is in use, try:
python manage.py runserver 8001
```

### Issue 2: "ModuleNotFoundError" when running Python script

**Solution:**
```bash
# Activate virtual environment first
cd C:\Users\admin\prompt-evaluator-and-optimizer
.\venv\Scripts\Activate.ps1

# Then run script
python test_preprocessor.py
```

### Issue 3: "Internal Server Error (500)"

**Solution:**
```bash
# Check server logs for errors
# Look at the terminal where runserver is running

# Or check Django logs:
cd backend
python manage.py runserver 2>&1 | tee server.log
```

### Issue 4: Database errors

**Solution:**
```bash
# Reset migrations if needed
cd backend
python manage.py migrate zero evaluator
python manage.py migrate
```

---

## Summary

**Preprocessor Agent Tests:**
- ✓ Normalizes whitespace
- ✓ Preserves original prompt
- ✓ Generates unique ID
- ✓ Extracts metadata (word count, timestamp)
- ✓ Feeds output to classifier

**Full Pipeline Tests:**
- ✓ Shows how all agents work together
- ✓ Shows iterative improvement (if needed)
- ✓ Shows final evaluation score and status
- ✓ Stores results in database

---

**Ready to test? Start with curl command or Python script above!**
