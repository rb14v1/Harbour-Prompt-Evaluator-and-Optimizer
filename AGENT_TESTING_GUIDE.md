# Agent Testing Guide - Complete Reference

How to check and inspect the output of each individual agent in the Prompt Evaluator pipeline.

---

## Table of Contents

1. [Pipeline Architecture](#pipeline-architecture)
2. [5 Testing Methods](#5-testing-methods)
3. [Data Flow Diagram](#data-flow-diagram)
4. [Agent Output Schemas](#agent-output-schemas)
5. [Complete Examples](#complete-examples)
6. [Sample Prompts & Outputs](#sample-prompts--outputs)
7. [Troubleshooting](#troubleshooting)

---

## Pipeline Architecture

### 7 Agents in Sequence

```
Raw User Prompt
    ↓
1. PREPROCESSOR → normalized prompt + metadata
    ↓
2. CLASSIFIER → task type + complexity
    ↓
3. ANALYZER → intent + requirements + context + constraints
    ↓
4. VALIDATOR → 8-dimension quality scores
    ↓
5. SCORING ENGINE → overall score (0-10) + status
    ↓
    ├─ Score ≥ 7.0? → REPORT AGENT → Final Result ✓
    └─ Score < 7.0? → IMPROVER (max 3 iterations)
                       ↓
                      Re-validate & Re-score
                       ↓
                      Loop back if intent preserved
    ↓
7. REPORT AGENT → Complete JSON Report
    ↓
Database (EvaluationResult.full_report)
    ↓
API Response (PromptEvaluationResponseSerializer)
```

---

## 5 Testing Methods

### ⚡ METHOD 1: Django Shell (Fastest for Quick Tests)

**When to use:** Testing single agent, ad-hoc debugging, quick verification

**File location:** Interactive shell (no file)

**Start:**
```bash
cd backend
python manage.py shell
```

**Test Preprocessor:**
```python
from evaluator.agents.preprocessor import PreprocessorAgent
import json

agent = PreprocessorAgent()
result = agent.process("Write a Python function that sorts arrays")
print(json.dumps(result, indent=2))
```

**Output:**
```json
{
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_prompt": "Write a Python function that sorts arrays",
  "processed_prompt": "Write a Python function that sorts arrays",
  "metadata": {
    "length": 7,
    "timestamp": "2026-09-10T14:30:00.123456",
    "version": 1
  }
}
```

**Test Classifier:**
```python
from evaluator.agents.classifier import ClassifierAgent

agent = ClassifierAgent()
result = agent.classify(result['processed_prompt'])
print(json.dumps(result, indent=2))
```

**Output:**
```json
{
  "task_type": "create_code",
  "complexity": "Simple",
  "confidence": 0.92,
  "reasoning": "Clear request to write a specific function with basic scope"
}
```

**Test Validator:**
```python
from evaluator.agents.validator import ValidatorAgent

agent = ValidatorAgent()
result = agent.validate("Write a Python function that sorts arrays")
print(json.dumps(result, indent=2))
```

**Output:**
```json
{
  "validation": {
    "clarity": {
      "level": "Good",
      "score": 7.5,
      "issues": [],
      "evidence": "Clear request with specific output expectation"
    },
    "specificity": {
      "level": "Moderate",
      "score": 5.0,
      "issues": ["No specification of sorting algorithm"],
      "evidence": "Type of sorting algorithm not specified"
    },
    "context": {
      "level": "Good",
      "score": 7.5,
      "issues": [],
      "evidence": "Context is clear from request"
    },
    "completeness": {
      "level": "Good",
      "score": 7.5,
      "issues": [],
      "evidence": "All necessary components present"
    },
    "requirements": {
      "level": "Moderate",
      "score": 5.0,
      "issues": ["No performance requirements specified"],
      "evidence": "No time/space complexity requirements"
    },
    "constraints": {
      "level": "Poor",
      "score": 2.5,
      "issues": ["No constraints defined"],
      "evidence": "No limitations or edge cases specified"
    },
    "expected_output": {
      "level": "Good",
      "score": 7.5,
      "issues": [],
      "evidence": "Expects a Python function implementation"
    },
    "actionability": {
      "level": "Good",
      "score": 7.5,
      "issues": [],
      "evidence": "Developer can immediately implement"
    }
  },
  "overall_issues": [
    "Algorithm choice not specified",
    "No performance requirements",
    "Edge cases not defined"
  ],
  "improvement_targets": ["specificity", "requirements", "constraints"]
}
```

**Test Scoring Engine:**
```python
from evaluator.agents.scoring_engine import ScoringEngine

engine = ScoringEngine()
result = engine.calculate_scores(validation_result['validation'])
print(json.dumps(result, indent=2))
```

**Output:**
```json
{
  "dimension_scores": {
    "clarity": 7.5,
    "specificity": 5.0,
    "context": 7.5,
    "completeness": 7.5,
    "requirements": 5.0,
    "constraints": 2.5,
    "expected_output": 7.5,
    "actionability": 7.5
  },
  "overall_score": 6.31,
  "threshold": 7.0,
  "status": "Needs Improvement",
  "low_scoring_dimensions": ["constraints", "specificity", "requirements"]
}
```

---

### 🐍 METHOD 2: Python Test Script (Reproducible & Shareable)

**When to use:** Testing full pipeline, reproducible results, sharing with team

**File location:** `backend/test_agents.py` (see end of guide for complete code)

**Run:**
```bash
cd backend
python test_agents.py
```

**Output:**
Shows all 7 agents' outputs in sequence with formatted JSON and data flow visualization.

**Advantages:**
- ✓ Reproducible - same prompt always same output
- ✓ Shareable - commit to git, run anytime
- ✓ Extensible - add more test prompts easily
- ✓ Compare outputs - see how different prompts flow through pipeline

---

### 🌐 METHOD 3: API Endpoint (Real-World Testing)

**When to use:** Testing full integration, how frontend uses it, real response format

**URL:** `POST http://localhost:8000/api/evaluations/evaluate/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "Write a Python function that sorts arrays"
}
```

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python function that sorts arrays"}'
```

**Response (Full Report):**
```json
{
  "original_prompt": "Write a Python function that sorts arrays",
  "classification": {
    "task_type": "create_code",
    "complexity": "Simple",
    "confidence": 0.92,
    "reasoning": "..."
  },
  "analysis": {
    "intent": "Create a Python function for sorting arrays",
    "requirements": [
      "Function must sort arrays",
      "Must be in Python"
    ],
    "context": [],
    "constraints": [],
    "expected_output": "Python function code",
    "missing_information": [
      "Sorting algorithm preference",
      "Performance requirements"
    ],
    "ambiguities": []
  },
  "initial_evaluation": {
    "dimension_scores": {
      "clarity": 7.5,
      "specificity": 5.0,
      "context": 7.5,
      "completeness": 7.5,
      "requirements": 5.0,
      "constraints": 2.5,
      "expected_output": 7.5,
      "actionability": 7.5
    },
    "overall_score": 6.31,
    "status": "Needs Improvement"
  },
  "improvement_history": [
    {
      "improved_prompt": "Write a Python function that implements the bubble sort algorithm to sort arrays in ascending order. The function should accept any size array and handle edge cases like empty arrays and arrays with one element.",
      "changes_made": [
        "Specified sorting algorithm (bubble sort)",
        "Added order specification (ascending)",
        "Added edge case handling",
        "Specified array size flexibility"
      ],
      "dimensions_addressed": ["specificity", "constraints", "requirements"],
      "intent_preserved": true,
      "iteration": 1,
      "reasoning": "Addressed 3 lowest-scoring dimensions"
    }
  ],
  "final_evaluation": {
    "dimension_scores": {
      "clarity": 8.5,
      "specificity": 8.0,
      "context": 8.0,
      "completeness": 8.5,
      "requirements": 8.0,
      "constraints": 7.5,
      "expected_output": 8.5,
      "actionability": 8.5
    },
    "overall_score": 8.19,
    "status": "Ready"
  },
  "final_prompt": "Write a Python function that implements the bubble sort algorithm to sort arrays in ascending order. The function should accept any size array and handle edge cases like empty arrays and arrays with one element.",
  "summary": "Prompt improved by 1.88 points (6.31 → 8.19) over 1 iteration. Status: Ready.",
  "status": "Ready",
  "improvements_made": 1,
  "iterations_required": 1,
  "timestamp": "2026-09-10T14:30:00.123456"
}
```

**Using Python:**
```python
import requests
import json

response = requests.post(
    'http://localhost:8000/api/evaluations/evaluate/',
    json={'prompt': 'Write a Python function that sorts arrays'}
)

result = response.json()
print(json.dumps(result, indent=2))
```

---

### 💾 METHOD 4: Database Query (Historical Analysis)

**When to use:** Inspecting stored results, verifying data persistence, analyzing history

**Start:**
```bash
cd backend
python manage.py shell
```

**Query Latest Evaluation:**
```python
from evaluator.models import EvaluationResult
import json

# Get latest evaluation
result = EvaluationResult.objects.latest('created_at')

# View full report
print(json.dumps(result.full_report, indent=2))

# View summary
print(f"Original Score: {result.initial_score}")
print(f"Final Score: {result.final_score}")
print(f"Improvements: {result.improvements_made}")
print(f"Status: {result.status}")
```

**Query All Evaluations for a Prompt:**
```python
from evaluator.models import Prompt

prompt = Prompt.objects.first()
results = prompt.result  # OneToOne relationship

print(f"Prompt: {prompt.original_prompt}")
print(f"Final Score: {results.final_score}")
print(f"Final Prompt: {results.final_prompt}")
```

**Export to JSON:**
```python
import json

result = EvaluationResult.objects.latest('created_at')
with open('evaluation_result.json', 'w') as f:
    json.dump(result.full_report, f, indent=2)
print("Exported to evaluation_result.json")
```

---

### 🚀 METHOD 5: curl REST Client (Scriptable)

**When to use:** Integration tests, shell scripts, CI/CD pipelines

**Basic Request:**
```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here"}'
```

**Save to File:**
```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here"}' > evaluation_result.json

# Pretty print
jq . evaluation_result.json
```

**Pretty Print:**
```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here"}' | jq '.'
```

**Extract Specific Agent Output:**
```bash
# Get initial classification
curl -s -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write code"}' | jq '.classification'

# Get final score
curl -s -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write code"}' | jq '.final_evaluation.overall_score'
```

---

## Data Flow Diagram

```
INPUT: Raw Prompt String
  │
  ├─ "Write a Python function that sorts arrays"
  │
  ▼
┌──────────────────────────────┐
│ 1. PREPROCESSOR AGENT        │
├──────────────────────────────┤
│ Input:  string               │
│ Output: {                    │
│   prompt_id: uuid,           │
│   original_prompt: string,   │
│   processed_prompt: string,  │
│   metadata: { ... }          │
│ }                            │
│ Time: <100ms                 │
└──────────────────────────────┘
  │
  ├─ prompt_id: "550e8400..."
  ├─ processed_prompt: "Write a Python function that sorts arrays"
  │
  ▼
┌──────────────────────────────┐
│ 2. CLASSIFIER AGENT          │
├──────────────────────────────┤
│ Input:  processed_prompt     │
│ Output: {                    │
│   task_type: string (9 cat), │
│   complexity: string (3 lvl),│
│   confidence: 0.0-1.0,       │
│   reasoning: string          │
│ }                            │
│ Time: 1-3s (Azure API)       │
└──────────────────────────────┘
  │
  ├─ task_type: "create_code"
  ├─ complexity: "Simple"
  ├─ confidence: 0.92
  │
  ▼
┌──────────────────────────────┐
│ 3. ANALYZER AGENT            │
├──────────────────────────────┤
│ Input:  processed_prompt,    │
│         task_type            │
│ Output: {                    │
│   intent: string,            │
│   requirements: [],          │
│   context: [],               │
│   constraints: [],           │
│   expected_output: string,   │
│   missing_info: [],          │
│   ambiguities: []            │
│ }                            │
│ Time: 2-4s (Azure API)       │
└──────────────────────────────┘
  │
  ├─ intent: "Create Python sort function"
  ├─ requirements: ["Function", "Sort", "Python"]
  ├─ missing_info: ["Algorithm", "Performance"]
  │
  ▼
┌──────────────────────────────┐
│ 4. VALIDATOR AGENT           │
├──────────────────────────────┤
│ Input:  processed_prompt,    │
│         analysis (optional)  │
│ Output: {                    │
│   validation: {              │
│     clarity: { score, ... }  │
│     specificity: { ... }     │
│     context: { ... }         │
│     completeness: { ... }    │
│     requirements: { ... }    │
│     constraints: { ... }     │
│     expected_output: { ... } │
│     actionability: { ... }   │
│   },                         │
│   overall_issues: [],        │
│   improvement_targets: []    │
│ }                            │
│ Time: 2-4s (Azure API)       │
└──────────────────────────────┘
  │
  ├─ clarity: { score: 7.5, level: "Good" }
  ├─ specificity: { score: 5.0, level: "Moderate" }
  ├─ constraints: { score: 2.5, level: "Poor" }
  │
  ▼
┌──────────────────────────────┐
│ 5. SCORING ENGINE            │
├──────────────────────────────┤
│ Input:  validation dict      │
│ Output: {                    │
│   dimension_scores: { ... }, │
│   overall_score: 0-10,       │
│   threshold: 7.0,            │
│   status: string,            │
│   low_scoring: [],           │
│   high_performing: []        │
│ }                            │
│ Time: <10ms                  │
└──────────────────────────────┘
  │
  ├─ overall_score: 6.31
  ├─ status: "Needs Improvement"
  ├─ low_scoring_dimensions: ["constraints", "specificity"]
  │
  ▼
  │
  ├─ Check: score (6.31) < threshold (7.0)? YES
  │
  ▼
┌──────────────────────────────┐
│ 6. IMPROVER AGENT            │
├──────────────────────────────┤
│ Input:  original_prompt,     │
│         analysis,            │
│         validation,          │
│         scoring,             │
│         iteration #          │
│ Output: {                    │
│   improved_prompt: string,   │
│   changes_made: [],          │
│   dimensions_addressed: [],  │
│   intent_preserved: bool,    │
│   iteration: int,            │
│   reasoning: string          │
│ }                            │
│ Time: 3-5s (Azure API)       │
└──────────────────────────────┘
  │
  ├─ improved_prompt: "Write a Python function..."
  ├─ changes_made: ["Added algorithm", "Added constraints"]
  ├─ intent_preserved: true
  │
  ▼
  │
  ├─ Loop back to Validator (max 3 iterations)
  ├─ Re-validate improved prompt
  ├─ Re-score
  ├─ Check: new_score (8.19) >= threshold (7.0)? YES → EXIT LOOP
  │
  ▼
┌──────────────────────────────┐
│ 7. REPORT AGENT              │
├──────────────────────────────┤
│ Input:  All prior outputs    │
│         Improvement history  │
│ Output: {                    │
│   original_prompt: string,   │
│   classification: { ... },   │
│   analysis: { ... },         │
│   initial_evaluation: { ... }│
│   improvement_history: [],   │
│   final_evaluation: { ... }, │
│   final_prompt: string,      │
│   summary: string,           │
│   status: string,            │
│   improvements_made: int,    │
│   iterations_required: int   │
│ }                            │
│ Time: <100ms                 │
└──────────────────────────────┘
  │
  ▼
┌──────────────────────────────┐
│ DATABASE: EvaluationResult   │
├──────────────────────────────┤
│ full_report: (JSON above)    │
│ final_score: 8.19            │
│ status: "Ready"              │
│ improvements_made: 1         │
└──────────────────────────────┘
  │
  ▼
┌──────────────────────────────┐
│ API RESPONSE (JSON above)    │
│ Frontend receives full       │
│ report with all agent data   │
└──────────────────────────────┘
```

---

## Agent Output Schemas

### 1. Preprocessor Output
```json
{
  "prompt_id": "string (UUID)",
  "original_prompt": "string (verbatim user input)",
  "processed_prompt": "string (normalized)",
  "metadata": {
    "length": "int (word count)",
    "timestamp": "string (ISO-8601)",
    "version": "int (always 1)"
  }
}
```

### 2. Classifier Output
```json
{
  "task_type": "string (one of 9 categories)",
  "complexity": "string (Simple|Moderate|Complex)",
  "confidence": "float (0.0-1.0)",
  "reasoning": "string (explanation)"
}
```

**Task Types (9):**
- `create_content` - Generate text/documents
- `create_code` - Write code
- `research` - Gather information
- `deep_research` - Extended research
- `plan_organize` - Structure projects
- `ideate` - Brainstorm ideas
- `summarize` - Condense text
- `explain` - Teach concepts
- `optimize` - Improve existing work

### 3. Analyzer Output
```json
{
  "intent": "string (main goal)",
  "requirements": ["string", "..."],
  "context": ["string", "..."],
  "constraints": ["string", "..."],
  "expected_output": "string (format/type)",
  "missing_information": ["string", "..."],
  "ambiguities": ["string", "..."]
}
```

### 4. Validator Output
```json
{
  "validation": {
    "clarity": {
      "level": "string (Poor|Moderate|Good|Excellent)",
      "score": "float (2.5|5.0|7.5|10.0)",
      "issues": ["string", "..."],
      "evidence": "string (why this score)"
    },
    "specificity": { "..." },
    "context": { "..." },
    "completeness": { "..." },
    "requirements": { "..." },
    "constraints": { "..." },
    "expected_output": { "..." },
    "actionability": { "..." }
  },
  "overall_issues": ["string", "..."],
  "improvement_targets": ["string (dimension names)", "..."]
}
```

### 5. Scoring Engine Output
```json
{
  "dimension_scores": {
    "clarity": "float (0-10)",
    "specificity": "float (0-10)",
    "context": "float (0-10)",
    "completeness": "float (0-10)",
    "requirements": "float (0-10)",
    "constraints": "float (0-10)",
    "expected_output": "float (0-10)",
    "actionability": "float (0-10)"
  },
  "overall_score": "float (0-10, average of dimensions)",
  "threshold": "float (7.0)",
  "status": "string (Needs Improvement|Ready)",
  "low_scoring_dimensions": ["string", "..."],
  "high_performing_dimensions": ["string", "..."]
}
```

### 6. Improver Output
```json
{
  "improved_prompt": "string (rewritten)",
  "changes_made": ["string", "..."],
  "dimensions_addressed": ["string", "..."],
  "intent_preserved": "bool (true|false)",
  "iteration": "int (1|2|3)",
  "reasoning": "string (why these changes)"
}
```

### 7. Report Output (Full Evaluation)
```json
{
  "prompt_id": "string (UUID)",
  "original_prompt": "string",
  "classification": { "..." },
  "analysis": { "..." },
  "initial_evaluation": { "..." },
  "improvement_history": [ { "..." } ],
  "final_evaluation": { "..." },
  "final_prompt": "string",
  "summary": "string (executive summary)",
  "status": "string (Ready|Needs Manual Review)",
  "improvements_made": "int (0-3)",
  "iterations_required": "int (0-3)",
  "timestamp": "string (ISO-8601)"
}
```

---

## Complete Examples

### Example 1: Simple Prompt (No Improvement Needed)

**Prompt:** `"Explain quantum computing in simple terms"`

**Flow:**
```
Preprocessor ✓ 
  → processed: "Explain quantum computing in simple terms"

Classifier ✓ 
  → task_type: "explain"
  → complexity: "Moderate"
  → confidence: 0.95

Analyzer ✓ 
  → intent: "Teach quantum computing concepts simply"
  → requirements: ["Simple explanation", "Quantum concepts"]
  → missing: ["Target audience level"]

Validator ✓ 
  → clarity: 8.5 (Good)
  → specificity: 7.5 (Good)
  → context: 8.0 (Good)
  → completeness: 8.0 (Good)
  → requirements: 8.5 (Good)
  → constraints: 7.0 (Good)
  → expected_output: 8.5 (Good)
  → actionability: 9.0 (Excellent)

Scoring Engine ✓ 
  → overall_score: 8.19 ≥ 7.0
  → status: "Ready"
  ✓ No improvement needed
  
Report ✓ 
  → improvements_made: 0
  → iterations_required: 0
  → status: "Ready"
```

---

### Example 2: Complex Prompt (Needs Improvement)

**Prompt:** `"Write code"`

**Flow:**
```
Preprocessor ✓ 
  → processed: "Write code"

Classifier ✓ 
  → task_type: "create_code"
  → complexity: "Simple"
  → confidence: 0.85

Analyzer ✓ 
  → intent: "Request to write code"
  → requirements: []
  → missing: ["Language", "Purpose", "Specifications"]
  → ambiguities: ["What kind of code?"]

Validator ✓ 
  → clarity: 5.0 (Moderate) - vague request
  → specificity: 2.5 (Poor) - no details
  → context: 2.5 (Poor) - no context
  → completeness: 3.0 (Poor) - missing key info
  → requirements: 2.5 (Poor) - no requirements
  → constraints: 2.5 (Poor) - no constraints
  → expected_output: 5.0 (Moderate) - assumes code
  → actionability: 3.0 (Poor) - can't execute

Scoring Engine ✓ 
  → overall_score: 3.38 < 7.0
  → status: "Needs Improvement"
  ✓ Trigger improvement loop
  
Improver (Iteration 1) ✓ 
  → improved: "Write a Python function that sorts arrays using merge sort"
  → changes: [
      "Added language (Python)",
      "Added task (function)",
      "Added algorithm (merge sort)",
      "Added data structure (arrays)"
    ]
  → dimensions_addressed: ["specificity", "context", "requirements"]
  → intent_preserved: true

Validator (Re-run) ✓ 
  → Now scores improve to 7.8 average
  
Scoring Engine (Re-run) ✓ 
  → overall_score: 7.8 ≥ 7.0
  → status: "Ready"
  ✓ Loop exits, improvement successful
  
Report ✓ 
  → improvements_made: 1
  → iterations_required: 1
  → status: "Ready"
```

---

## Sample Prompts & Outputs

### Sample 1: E-commerce Product Description

**Input Prompt:**
```
Generate a product description
```

**Preprocessor Output:**
```json
{
  "prompt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "original_prompt": "Generate a product description",
  "processed_prompt": "Generate a product description",
  "metadata": {
    "length": 4,
    "timestamp": "2026-09-10T14:35:22.456789",
    "version": 1
  }
}
```

**Classifier Output:**
```json
{
  "task_type": "create_content",
  "complexity": "Simple",
  "confidence": 0.88,
  "reasoning": "Generic request for content creation with limited scope"
}
```

**Analyzer Output:**
```json
{
  "intent": "Create marketing content for product",
  "requirements": [
    "Must be description format",
    "Must describe product"
  ],
  "context": [],
  "constraints": [],
  "expected_output": "Product description text",
  "missing_information": [
    "Product type/category",
    "Target audience",
    "Tone (formal/casual)",
    "Length requirements",
    "Key features to highlight"
  ],
  "ambiguities": [
    "Which product?",
    "What format? (short/long/bullet points?)"
  ]
}
```

**Validator Output (Initial):**
```json
{
  "validation": {
    "clarity": {
      "level": "Moderate",
      "score": 5.0,
      "issues": ["No specific product mentioned"],
      "evidence": "Request refers to generic 'product' without identification"
    },
    "specificity": {
      "level": "Poor",
      "score": 2.5,
      "issues": [
        "No product type specified",
        "No target audience specified",
        "No format specified"
      ],
      "evidence": "One word subject with no qualifiers or details"
    },
    "context": {
      "level": "Poor",
      "score": 2.5,
      "issues": ["No context about product, market, or audience"],
      "evidence": "Completely absent"
    },
    "completeness": {
      "level": "Moderate",
      "score": 5.0,
      "issues": ["Key information missing"],
      "evidence": "Only verb and noun, no details"
    },
    "requirements": {
      "level": "Moderate",
      "score": 5.0,
      "issues": ["No success criteria defined"],
      "evidence": "What makes a good description here?"
    },
    "constraints": {
      "level": "Poor",
      "score": 2.5,
      "issues": ["No constraints specified"],
      "evidence": "No length, tone, or format constraints"
    },
    "expected_output": {
      "level": "Moderate",
      "score": 5.0,
      "issues": ["Format not specified"],
      "evidence": "Assumes text, but length/structure unclear"
    },
    "actionability": {
      "level": "Poor",
      "score": 2.5,
      "issues": ["Cannot execute without clarification"],
      "evidence": "Too vague to produce useful output"
    }
  },
  "overall_issues": [
    "Vague product reference",
    "Missing target audience",
    "No format specification",
    "No tone or style guidance",
    "No length requirements"
  ],
  "improvement_targets": [
    "specificity",
    "context",
    "constraints",
    "actionability"
  ]
}
```

**Scoring Engine Output (Initial):**
```json
{
  "dimension_scores": {
    "clarity": 5.0,
    "specificity": 2.5,
    "context": 2.5,
    "completeness": 5.0,
    "requirements": 5.0,
    "constraints": 2.5,
    "expected_output": 5.0,
    "actionability": 2.5
  },
  "overall_score": 3.81,
  "threshold": 7.0,
  "status": "Needs Improvement",
  "low_scoring_dimensions": [
    "specificity",
    "context",
    "constraints",
    "actionability"
  ],
  "high_performing_dimensions": []
}
```

**Improver Output (Iteration 1):**
```json
{
  "improved_prompt": "Write a product description for a premium leather handbag. Target audience: professional women aged 25-45 with high disposable income. Tone: sophisticated and aspirational. Length: 150-200 words. Highlight: craftsmanship, durability, style versatility, and brand heritage. Format: compelling opening sentence, 2-3 benefit-focused paragraphs, closing call-to-action.",
  "changes_made": [
    "Specified product type and quality level (premium leather handbag)",
    "Added target audience (professional women 25-45)",
    "Specified tone (sophisticated, aspirational)",
    "Added length requirement (150-200 words)",
    "Listed key features to highlight",
    "Specified format structure",
    "Added call-to-action requirement"
  ],
  "dimensions_addressed": [
    "specificity",
    "context",
    "constraints",
    "actionability"
  ],
  "intent_preserved": true,
  "iteration": 1,
  "reasoning": "Addressed 4 lowest-scoring dimensions by providing concrete product details, audience parameters, tone guidance, and structural requirements"
}
```

**Validator Output (After Improvement):**
```json
{
  "validation": {
    "clarity": {
      "level": "Excellent",
      "score": 10.0,
      "issues": [],
      "evidence": "Specific product, audience, and purpose clearly defined"
    },
    "specificity": {
      "level": "Excellent",
      "score": 10.0,
      "issues": [],
      "evidence": "All parameters precisely specified"
    },
    "context": {
      "level": "Excellent",
      "score": 10.0,
      "issues": [],
      "evidence": "Target audience and market positioning clearly defined"
    },
    "completeness": {
      "level": "Excellent",
      "score": 10.0,
      "issues": [],
      "evidence": "All necessary components present"
    },
    "requirements": {
      "level": "Excellent",
      "score": 10.0,
      "issues": [],
      "evidence": "Clear success criteria and deliverables"
    },
    "constraints": {
      "level": "Good",
      "score": 7.5,
      "issues": [],
      "evidence": "Length and format constraints specified"
    },
    "expected_output": {
      "level": "Excellent",
      "score": 10.0,
      "issues": [],
      "evidence": "Output format and structure clearly defined"
    },
    "actionability": {
      "level": "Excellent",
      "score": 10.0,
      "issues": [],
      "evidence": "Writer can immediately execute"
    }
  },
  "overall_issues": [],
  "improvement_targets": []
}
```

**Scoring Engine Output (After Improvement):**
```json
{
  "dimension_scores": {
    "clarity": 10.0,
    "specificity": 10.0,
    "context": 10.0,
    "completeness": 10.0,
    "requirements": 10.0,
    "constraints": 7.5,
    "expected_output": 10.0,
    "actionability": 10.0
  },
  "overall_score": 9.69,
  "threshold": 7.0,
  "status": "Ready",
  "low_scoring_dimensions": [],
  "high_performing_dimensions": [
    "clarity",
    "specificity",
    "context",
    "completeness",
    "requirements",
    "expected_output",
    "actionability"
  ]
}
```

**Report Output (Final):**
```json
{
  "prompt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "original_prompt": "Generate a product description",
  "classification": {
    "task_type": "create_content",
    "complexity": "Simple",
    "confidence": 0.88,
    "reasoning": "Generic request for content creation with limited scope"
  },
  "analysis": {
    "intent": "Create marketing content for product",
    "requirements": [
      "Must be description format",
      "Must describe product"
    ],
    "context": [],
    "constraints": [],
    "expected_output": "Product description text",
    "missing_information": [
      "Product type/category",
      "Target audience",
      "Tone (formal/casual)",
      "Length requirements",
      "Key features to highlight"
    ],
    "ambiguities": [
      "Which product?",
      "What format? (short/long/bullet points?)"
    ]
  },
  "initial_evaluation": {
    "dimension_scores": {
      "clarity": 5.0,
      "specificity": 2.5,
      "context": 2.5,
      "completeness": 5.0,
      "requirements": 5.0,
      "constraints": 2.5,
      "expected_output": 5.0,
      "actionability": 2.5
    },
    "overall_score": 3.81,
    "status": "Needs Improvement",
    "low_scoring_dimensions": ["specificity", "context", "constraints", "actionability"]
  },
  "improvement_history": [
    {
      "improved_prompt": "Write a product description for a premium leather handbag. Target audience: professional women aged 25-45 with high disposable income. Tone: sophisticated and aspirational. Length: 150-200 words. Highlight: craftsmanship, durability, style versatility, and brand heritage. Format: compelling opening sentence, 2-3 benefit-focused paragraphs, closing call-to-action.",
      "changes_made": [
        "Specified product type and quality level (premium leather handbag)",
        "Added target audience (professional women 25-45)",
        "Specified tone (sophisticated, aspirational)",
        "Added length requirement (150-200 words)",
        "Listed key features to highlight",
        "Specified format structure",
        "Added call-to-action requirement"
      ],
      "dimensions_addressed": ["specificity", "context", "constraints", "actionability"],
      "intent_preserved": true,
      "iteration": 1,
      "reasoning": "Addressed 4 lowest-scoring dimensions by providing concrete product details, audience parameters, tone guidance, and structural requirements"
    }
  ],
  "final_evaluation": {
    "dimension_scores": {
      "clarity": 10.0,
      "specificity": 10.0,
      "context": 10.0,
      "completeness": 10.0,
      "requirements": 10.0,
      "constraints": 7.5,
      "expected_output": 10.0,
      "actionability": 10.0
    },
    "overall_score": 9.69,
    "status": "Ready",
    "high_performing_dimensions": [
      "clarity",
      "specificity",
      "context",
      "completeness",
      "requirements",
      "expected_output",
      "actionability"
    ]
  },
  "final_prompt": "Write a product description for a premium leather handbag. Target audience: professional women aged 25-45 with high disposable income. Tone: sophisticated and aspirational. Length: 150-200 words. Highlight: craftsmanship, durability, style versatility, and brand heritage. Format: compelling opening sentence, 2-3 benefit-focused paragraphs, closing call-to-action.",
  "summary": "Prompt improved dramatically by 5.88 points (3.81 → 9.69) over 1 iteration. All critical specifications added: product details, target audience, tone, length, and format. Status: Ready for immediate use.",
  "status": "Ready",
  "improvements_made": 1,
  "iterations_required": 1,
  "timestamp": "2026-09-10T14:35:45.123456"
}
```

---

## Troubleshooting

### Issue: ImportError when testing agents

**Problem:**
```
ImportError: No module named 'evaluator.agents.preprocessor'
```

**Solution:**
1. Verify you're in `backend` directory
2. Check `backend/evaluator/agents/` exists
3. Verify `__init__.py` files exist in all directories
4. Run from backend folder: `python manage.py shell`

### Issue: Azure API timeout/error

**Problem:**
```
RequestException: Connection timeout
```

**Solution:**
1. Check .env has valid `AZURE_OPENAI_API_KEY`
2. Verify network connection
3. Check Azure API is reachable
4. Add retry logic for production

### Issue: Database errors

**Problem:**
```
OperationalError: no such table: evaluator_evaluationresult
```

**Solution:**
1. Run migrations: `python manage.py migrate`
2. Verify database exists: `python manage.py shell`
3. Check database settings in `settings.py`

### Issue: JSON serialization error

**Problem:**
```
TypeError: Object is not JSON serializable
```

**Solution:**
1. Use `json.dumps()` with `default=str` for datetime objects
2. Verify all agent outputs are JSON-compatible
3. Use `cls=DjangoJSONEncoder` for Django models

### Issue: API returns 404

**Problem:**
```
{
  "detail": "Not found."
}
```

**Solution:**
1. Check backend is running on port 8000
2. Verify API URL: `http://localhost:8000/api/evaluations/evaluate/`
3. Check request method is POST (not GET)
4. Verify JSON content-type header

---

## Next Steps

1. **Choose a testing method** from the 5 options above
2. **Run with sample prompt** from "Sample Prompts & Outputs"
3. **Compare outputs** across methods (should match)
4. **Trace data flow** through all 7 agents
5. **Export results** to JSON for analysis

---

**Last Updated:** 2026-09-10  
**Status:** ✅ Complete
