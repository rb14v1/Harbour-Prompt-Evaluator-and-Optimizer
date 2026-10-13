# How to Check Outputs for a New Prompt

Complete guide for testing the Prompt Evaluator and Optimizer backend.

---

## 📖 Overview

You have **two testing approaches**:

1. **Preprocessor Agent in Isolation** - Test just text normalization
2. **Full Pipeline with API** - Submit prompt and get complete evaluation

Both can be tested using **curl commands** (fastest and simplest).

---

## 🚀 Quickest Way to Start (3 Steps)

### Step 1: Start Server (Terminal 1)

```bash
cd C:\Users\admin\prompt-evaluator-and-optimizer\backend
..\venv\Scripts\Activate.ps1
python manage.py runserver
```

Wait for: `Starting development server at http://127.0.0.1:8000/`

### Step 2: Test Preprocessor (Terminal 2)

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python function"}'
```

### Step 3: View Results

- **In Terminal 2**: JSON output shows all agent results
- **In Browser**: http://localhost:8000/admin (admin/admin123)
- **In Database**: All evaluations stored and searchable

---

## 📋 What Gets Tested

### Preprocessor Agent Tests

The preprocessor handles:
- ✓ Text normalization (removes extra whitespace)
- ✓ Original prompt preservation (keeps exact input)
- ✓ Metadata extraction (counts words, timestamps)
- ✓ Unique ID generation (for tracking)

**Example:**
```
Input:  "Write   a   Python   function"
Output: "Write a Python function"
```

### Full Pipeline Tests

The complete pipeline includes:
1. **Preprocessor** → Normalize text
2. **Classifier** → Categorize task (9 types)
3. **Analyzer** → Extract components (intent, requirements, context)
4. **Validator** → Score 8 dimensions
5. **Scorer** → Calculate overall score (threshold: 7.0)
6. **Improver** (optional) → Improve if score < 7.0 (max 3 iterations)
7. **Reporter** → Generate final report

---

## 🧪 Testing Methods

### Method 1: Via curl (Recommended - Fastest)

**See preprocessor + full pipeline in one call:**

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python function that sorts arrays"}'
```

**Response includes:**
- prompt_id (from preprocessor)
- original_prompt (from preprocessor)
- processed_prompt (normalized by preprocessor)
- classification (from classifier)
- analysis (from analyzer)
- initial_evaluation (from validator)
- final_evaluation (from scorer)
- improvement_history (from improver if applicable)
- final_prompt (best version)
- status (Ready or Needs Manual Review)

### Method 2: Test Preprocessor Only

Create file `test_preprocessor.py`:

```python
from evaluator.agents.preprocessor import PreprocessorAgent
import json

agent = PreprocessorAgent()
result = agent.process("Write   a   Python   function")
print(json.dumps(result, indent=2))
```

Run:
```bash
cd backend
..\venv\Scripts\Activate.ps1
python test_preprocessor.py
```

### Method 3: Django Admin

```
http://localhost:8000/admin
Username: admin
Password: admin123
```

Browse all evaluations and see:
- Prompts submitted
- Classifications (task type, complexity)
- Analyses (intent, requirements, context)
- Evaluations (dimension scores)
- Results (final scores, status)

### Method 4: Django Shell

```bash
cd backend
python manage.py shell
```

```python
from evaluator.models import EvaluationResult
latest = EvaluationResult.objects.latest('created_at')
print(latest.original_prompt)
print(latest.final_score)
print(latest.status)
```

---

## 📊 Understanding the Response

### Preprocessor Output (Part of Full Response)

Located in response under these fields:

```json
{
  "prompt_id": "unique-id-for-tracking",
  "original_prompt": "exact input (unchanged)",
  "final_prompt": "best version after all improvements",
  "classification": {
    "task_type": "Create Code",
    "complexity": "Moderate",
    "confidence": 0.95
  }
}
```

### Scoring Breakdown (8 Dimensions)

```json
{
  "dimension_scores": {
    "clarity": 7.5,           // Is request clear?
    "specificity": 5.0,       // Is enough detail provided?
    "context": 7.5,           // Is background included?
    "completeness": 7.5,      // Are all components present?
    "requirements": 5.0,      // Are success criteria explicit?
    "constraints": 7.5,       // Are boundaries defined?
    "expected_output": 7.5,   // Is output format clear?
    "actionability": 5.0      // Can it be executed now?
  },
  "overall_score": 6.56,      // Average of 8 dimensions
  "threshold": 7.0,           // Minimum passing score
  "status": "Needs Improvement"
}
```

**Score Scale:**
- 2.5 = Poor (major gaps)
- 5.0 = Moderate (some issues)
- 7.5 = Good (solid, minor refinements)
- 10.0 = Excellent (ready to use)

### Improvement Results (If Applicable)

When score < 7.0, prompt is automatically improved:

```json
{
  "improvements_made": 1,
  "iterations_required": 1,
  "improvement_history": [
    {
      "iteration": 1,
      "improved_prompt": "Original prompt + improvements",
      "changes_made": [
        "Added language specification",
        "Specified function name",
        "Defined input/output types"
      ],
      "dimensions_addressed": ["specificity", "requirements"]
    }
  ],
  "final_score": 8.75,
  "status": "Ready"
}
```

---

## 🎯 Test Scenarios

### Scenario 1: High-Quality Prompt (No Improvement Needed)

**Input:**
```json
{"prompt": "Write a Python function named calculate_total that takes a list of numbers and returns their sum using the built-in sum() function"}
```

**Expected Output:**
```json
{
  "initial_score": 9.0,
  "final_score": 9.0,
  "improvements_made": 0,
  "status": "Ready",
  "summary": "Excellent prompt. All criteria met. Ready for execution."
}
```

### Scenario 2: Vague Prompt (Needs Improvement)

**Input:**
```json
{"prompt": "Create a function"}
```

**Expected Output:**
```json
{
  "initial_score": 2.5,
  "final_score": 8.2,
  "improvements_made": 1,
  "iterations_required": 1,
  "status": "Ready",
  "summary": "Prompt significantly improved. Added specific details, requirements, and expected output."
}
```

### Scenario 3: Medium Prompt (Small Improvement)

**Input:**
```json
{"prompt": "Design a database schema"}
```

**Expected Output:**
```json
{
  "initial_score": 5.0,
  "final_score": 7.5,
  "improvements_made": 1,
  "iterations_required": 1,
  "status": "Ready"
}
```

---

## 🔍 Verification Checklist

After testing, verify:

- [ ] **Preprocessor working**
  - [ ] Original prompt preserved exactly
  - [ ] Whitespace normalized correctly
  - [ ] Unique ID generated
  - [ ] Metadata extracted (word count, timestamp)

- [ ] **Full pipeline working**
  - [ ] Classification detects task type correctly
  - [ ] Analysis extracts requirements and constraints
  - [ ] Validator scores all 8 dimensions
  - [ ] Scorer calculates overall score
  - [ ] Good prompts get "Ready" status
  - [ ] Vague prompts trigger improvements

- [ ] **Database working**
  - [ ] Results saved to database
  - [ ] Admin panel shows results
  - [ ] Can query results via Django shell
  - [ ] Multiple evaluations tracked separately

- [ ] **Improvements working**
  - [ ] Vague prompts get improved
  - [ ] Max 3 iterations enforced
  - [ ] Intent preserved (checked)
  - [ ] Score increases after improvement
  - [ ] Changes documented

---

## 📚 Related Documents

| Document | Purpose |
|----------|---------|
| **QUICK_TEST_REFERENCE.md** | Copy-paste commands (fastest) |
| **TESTING_GUIDE.md** | Detailed guide with examples |
| **README.md** | Project overview and user guide |
| **CLAUDE.md** | Technical architecture |
| **SETUP.md** | Installation and configuration |

---

## 🐛 Troubleshooting

### "Connection refused"
```bash
# Make sure server is running
cd backend
python manage.py runserver
```

### "ModuleNotFoundError"
```bash
# Activate virtual environment
..\venv\Scripts\Activate.ps1
```

### "Database error"
```bash
# Reset database
cd backend
python manage.py migrate
```

### "Port 8000 in use"
```bash
# Use different port
python manage.py runserver 8001
```

---

## ✨ What You'll Learn

After testing, you'll understand:

1. **How Preprocessor normalizes text**
   - Removes extra whitespace
   - Preserves original for reference
   - Extracts metadata

2. **How full pipeline works**
   - Data flows through 7 agents
   - Each agent outputs specific results
   - Results compound into final evaluation

3. **How scoring works**
   - 8 dimensions evaluated independently
   - Overall score is average of dimensions
   - 7.0 threshold determines if improvement needed

4. **How improvement works**
   - Automatic rewriting if score < 7.0
   - Max 3 iterations to reach threshold
   - Intent preservation verified

5. **How results are stored**
   - Evaluations persisted in database
   - Complete history maintained
   - Admin interface for browsing

---

## 🚀 Ready to Test?

**Quickest path:**

1. Open Terminal 1
   ```bash
   cd C:\Users\admin\prompt-evaluator-and-optimizer\backend
   ..\venv\Scripts\Activate.ps1
   python manage.py runserver
   ```

2. Open Terminal 2
   ```bash
   curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Write a function that sorts arrays"}'
   ```

3. See results in JSON output

4. Visit http://localhost:8000/admin to browse database

**That's it! You're testing the system.**

---

## 📞 Need Help?

- **Quick commands?** → See `QUICK_TEST_REFERENCE.md`
- **Detailed guide?** → See `TESTING_GUIDE.md`
- **How to set up?** → See `SETUP.md`
- **Architecture?** → See `CLAUDE.md`

---

**Preprocessor output is part of every evaluation result. It normalizes your prompt and feeds it to the next agent. Together with 6 other agents, it creates a comprehensive evaluation with improvement suggestions!**

Happy testing! 🎉
