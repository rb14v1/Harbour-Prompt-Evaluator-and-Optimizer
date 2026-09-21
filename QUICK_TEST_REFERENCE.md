# Quick Test Reference Card

## 🚀 Quick Start (Copy & Paste Commands)

### Terminal 1: Start Server

```bash
cd C:\Users\admin\prompt-evaluator-and-optimizer\backend
..\venv\Scripts\Activate.ps1
python manage.py runserver
```

Expected output:
```
Starting development server at http://127.0.0.1:8000/
```

---

### Terminal 2: Test Preprocessor Isolation

**Option A: Python Script (Recommended)**

```bash
cd C:\Users\admin\prompt-evaluator-and-optimizer\backend
..\venv\Scripts\Activate.ps1
python << 'EOF'
from evaluator.agents.preprocessor import PreprocessorAgent
import json

agent = PreprocessorAgent()
result = agent.process("Write   a   Python   function")
print(json.dumps(result, indent=2))
EOF
```

**Option B: Django Shell**

```bash
cd backend
python manage.py shell
```

Then in shell:
```python
from evaluator.agents.preprocessor import PreprocessorAgent
agent = PreprocessorAgent()
result = agent.process("Write   a   Python   function")
print(result)
```

---

### Terminal 2: Test Full Pipeline with curl

**Test 1: Simple Prompt**

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a function that sorts arrays"}'
```

**Test 2: Vague Prompt (will trigger improvements)**

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a function"}'
```

**Test 3: Complex Prompt**

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Django REST API endpoint that handles CRUD operations for a blog app with proper authentication, validation, and comprehensive documentation"}'
```

**Test 4: Batch (multiple prompts)**

```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompts": ["Write a function", "Create an API", "Design a database"]}'
```

---

## 📊 Interpreting Results

### What Each Agent Does

| Agent | Input | Output | What to Look For |
|-------|-------|--------|------------------|
| Preprocessor | Raw prompt | Normalized text + metadata | `processed_prompt` should have extra spaces removed |
| Classifier | Normalized prompt | Task type, complexity, confidence | `confidence` should be > 0.7 for good classification |
| Analyzer | Processed prompt | Intent, requirements, constraints | Should capture what you asked for |
| Validator | Analyzed prompt | 8 dimension scores | All scores should be between 2.5 - 10.0 |
| Scorer | Validation results | Overall score | Score ≥ 7.0 = "Ready", < 7.0 = "Needs Improvement" |
| Improver | Low scores | Rewritten prompt | Only runs if score < 7.0, max 3 iterations |
| Report | All results | Final report | Complete evaluation with summary |

### Key Numbers in Response

```json
{
  "original_score": "float (2.5-10.0)",      // Score of original prompt
  "final_score": "float (2.5-10.0)",         // Score after improvement (or same if ready)
  "improvements_made": "int (0-3)",          // How many times it was improved
  "iterations_required": "int (0-3)",        // How many improvement cycles
  "status": "Ready | Needs Manual Review",   // Overall status
  "threshold": 7.0                           // Minimum passing score
}
```

---

## 🔍 Check Database

### Admin Interface

```
URL: http://localhost:8000/admin
User: admin
Pass: admin123
```

Browse:
- Prompts
- Classifications
- Analyses
- Evaluations
- Results

### Django Shell

```bash
cd backend
python manage.py shell
```

```python
from evaluator.models import EvaluationResult, Prompt

# Get latest result
latest = EvaluationResult.objects.latest('created_at')
print(f"Original: {latest.original_prompt}")
print(f"Final: {latest.final_prompt}")
print(f"Score: {latest.final_score}")
print(f"Status: {latest.status}")

# See all results
results = EvaluationResult.objects.all()
for r in results:
    print(f"{r.original_prompt[:40]}... → {r.final_score}")
```

---

## 📋 Expected Outputs

### Preprocessor Output (Isolation)

```json
{
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_prompt": "Write   a   Python   function",
  "processed_prompt": "Write a Python function",
  "metadata": {
    "length": 4,
    "timestamp": "2026-09-10T15:30:45.123456Z",
    "version": 1
  }
}
```

### Full Pipeline Response (Summary)

```json
{
  "prompt_id": "550e8400...",
  "original_prompt": "Your prompt...",
  "classification": {
    "task_type": "Create Code",
    "complexity": "Moderate",
    "confidence": 0.92
  },
  "analysis": {
    "intent": "Write Python code...",
    "requirements": [...],
    "constraints": [...]
  },
  "initial_evaluation": {
    "overall_score": 7.5,
    "status": "Ready"
  },
  "final_evaluation": {
    "overall_score": 7.5,
    "status": "Ready"
  },
  "summary": "Prompt is clear...",
  "status": "Ready",
  "improvements_made": 0,
  "timestamp": "2026-09-10T15:30:45.123456Z"
}
```

---

## ✅ Testing Checklist

- [ ] Server running on http://localhost:8000
- [ ] Can access admin at http://localhost:8000/admin
- [ ] Preprocessor normalizes whitespace ✓
- [ ] Classifier detects task type ✓
- [ ] Analyzer extracts components ✓
- [ ] Validator scores all 8 dimensions ✓
- [ ] Scorer calculates overall score ✓
- [ ] Good prompts get "Ready" status ✓
- [ ] Vague prompts trigger improvements ✓
- [ ] Results saved to database ✓

---

## 🐛 Common Issues

| Issue | Fix |
|-------|-----|
| Connection refused | Start server: `python manage.py runserver` |
| 404 Not found | Check URL: `http://localhost:8000/api/evaluations/evaluate/` |
| 500 Internal error | Check server logs for errors |
| venv not found | Activate first: `..\venv\Scripts\Activate.ps1` |
| ModuleNotFoundError | Make sure virtual env is activated |
| Database errors | Reset: `python manage.py migrate` |

---

## 📚 Full Guides

- Detailed guide: `TESTING_GUIDE.md`
- API documentation: `README.md`
- Architecture: `CLAUDE.md`
- Setup: `SETUP.md`

---

## 🎯 Next Steps

1. Start server in Terminal 1
2. Run test in Terminal 2
3. Check results
4. Access admin panel
5. View database

**Let's test!** 🚀
