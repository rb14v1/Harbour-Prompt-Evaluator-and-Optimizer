# Agent Testing Implementation - Summary

Complete solution for testing and inspecting individual agent outputs in the Prompt Evaluator pipeline.

---

## What Was Delivered

### 1. **AGENT_TESTING_GUIDE.md** (600+ lines)

Comprehensive reference guide with:

✅ **5 Complete Testing Methods**
- Method 1: Django Shell (quick ad-hoc testing)
- Method 2: Python Test Script (reproducible)
- Method 3: API Endpoint (real-world integration)
- Method 4: Database Query (historical analysis)
- Method 5: curl REST Client (scriptable)

Each method includes:
- Step-by-step instructions
- Complete working examples
- Copy-paste ready commands
- Expected outputs with real data
- When to use each method

✅ **Pipeline Architecture**
- ASCII diagram showing all 7 agents
- Sequential flow with decision points
- Data passing between stages
- Improvement loop logic

✅ **Agent Output Schemas**
All 7 agent outputs documented:
1. Preprocessor → {prompt_id, processed_prompt, metadata}
2. Classifier → {task_type, complexity, confidence}
3. Analyzer → {intent, requirements, context, constraints}
4. Validator → {8-dimension scores, issues, targets}
5. Scoring Engine → {dimension_scores, overall_score, status}
6. Improver → {improved_prompt, changes, iteration}
7. Report → {complete evaluation report}

✅ **Data Flow Diagrams**
- Detailed ASCII flow showing input→output
- Each stage's processing
- How data passes between agents
- Score calculation and thresholds
- Improvement loop decisions

✅ **Complete Examples**
2 detailed examples:
1. **Simple Prompt** - No improvement needed (score ≥ 7.0)
2. **Complex Prompt** - Requires improvement (score < 7.0)
   - Shows initial evaluation
   - Shows improvement suggestions
   - Shows re-evaluation
   - Final successful result

✅ **Sample Outputs**
Real example: "Generate a product description"
- Shows progression through all 7 agents
- Initial score: 3.81 (needs improvement)
- After iteration 1: 9.69 (ready)
- Complete JSON at each stage

✅ **Troubleshooting Guide**
- ImportError solutions
- Azure API timeout fixes
- Database error resolution
- JSON serialization issues
- API connection problems

---

### 2. **backend/test_agents.py** (350+ lines)

Executable Python script demonstrating all methods:

**Usage:**
```bash
cd backend
python test_agents.py                    # Run all methods
python test_agents.py --method 1         # Test only method 1
python test_agents.py --export           # Export to JSON
python test_agents.py --prompt "Your prompt"
```

**Features:**

✅ **Method 1: Django Shell Simulation**
- Tests each agent individually
- Shows preprocessing → classification → analysis → validation → scoring
- Optional: Shows improver if score < 7.0
- Displays output at each stage
- Formatted JSON output

✅ **Method 2: Full Pipeline**
- Runs complete orchestrator.evaluate()
- Shows overall metrics
- Pipeline execution summary
- Final report

✅ **Method 3: API Endpoint Simulation**
- Simulates POST request
- Shows request/response format
- API serializer output

✅ **Method 4: Database Query**
- Queries latest evaluation from database
- Shows stored full_report JSON
- Retrieves historical data

✅ **Method 5: Data Flow Visualization**
- ASCII visualization of pipeline
- Shows data at each stage
- Input/output for each agent
- Decision point (improvement needed?)
- Storage and API output

✅ **Comparison Across Methods**
- Verifies same data across methods
- Checks consistency
- Validates agent outputs

✅ **Export to JSON**
- Saves results to individual JSON files
- One file per method
- Organized in `test_results/` directory
- Numbered for easy reference

---

## 7 Agents in the Pipeline

### Overview

```
Raw Prompt
    ↓
Preprocessor   (normalize, generate UUID)
    ↓
Classifier     (categorize, assess complexity)
    ↓
Analyzer       (decompose into components)
    ↓
Validator      (score across 8 dimensions)
    ↓
Scoring Engine (calculate overall score)
    ↓
    ├─ Score ≥ 7.0? → Report (READY)
    └─ Score < 7.0? → Improver → Validator → Scorer (LOOP max 3x)
    ↓
Report Agent   (aggregate and format)
    ↓
EvaluationResult (stored in database)
    ↓
API Response   (sent to frontend)
```

### Agent Outputs Quick Reference

| Agent | Input | Output | Time |
|-------|-------|--------|------|
| **Preprocessor** | Raw string | {prompt_id, processed_prompt, metadata} | <100ms |
| **Classifier** | String | {task_type, complexity, confidence} | 1-3s |
| **Analyzer** | String | {intent, requirements[], context[]} | 2-4s |
| **Validator** | String | {validation{8_dims}, issues[], targets[]} | 2-4s |
| **ScoringEngine** | Validation | {dimension_scores, overall_score, status} | <10ms |
| **Improver** | Prompt+analysis | {improved_prompt, changes[], iteration} | 3-5s |
| **Report** | All outputs | {complete report} | <100ms |

---

## Quick Start

### Run All Tests
```bash
cd backend
python test_agents.py
```

Expected output:
- Individual agent outputs (Method 1)
- Full pipeline result (Method 2)
- API simulation (Method 3)
- Database query (Method 4)
- Data flow visualization (Method 5)
- Cross-method comparison

### Test Specific Agent
```bash
cd backend
python manage.py shell
```

Then:
```python
from evaluator.agents.preprocessor import PreprocessorAgent
agent = PreprocessorAgent()
result = agent.process("Your prompt")
print(result)
```

### Test Full Pipeline via API
```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here"}'
```

### Export Results
```bash
cd backend
python test_agents.py --export
# Creates test_results/ directory with JSON files
```

---

## 8 Validation Dimensions

Every prompt is scored across these 8 dimensions (each scored 0-10):

1. **Clarity** - Is the request unambiguous and easy to understand?
2. **Specificity** - Is enough detail provided to guide execution?
3. **Context** - Is relevant background information included?
4. **Completeness** - Are all necessary components present?
5. **Requirements** - Are success criteria explicit?
6. **Constraints** - Are limitations/boundaries defined?
7. **Expected Output** - Is desired output format clear?
8. **Actionability** - Can it be executed immediately?

**Scoring:**
- Poor: 2.5 (major gaps)
- Moderate: 5.0 (some issues)
- Good: 7.5 (solid, minor refinements)
- Excellent: 10.0 (exemplary)

**Overall Score = Average of 8 dimensions**  
**Threshold = 7.0 (must reach to be "Ready")**

---

## Data Flow Example

**Input:** `"Write a Python function that sorts arrays"`

### Stage 1: Preprocessor
```
Input:  "Write a Python function that sorts arrays"
Output: {
  prompt_id: "550e8400-e29b-41d4-a716-446655440000",
  original_prompt: "Write a Python function that sorts arrays",
  processed_prompt: "Write a Python function that sorts arrays",
  metadata: { length: 7, timestamp: "2026-09-10T14:30:00", version: 1 }
}
```

### Stage 2: Classifier
```
Input:  "Write a Python function that sorts arrays"
Output: {
  task_type: "create_code",
  complexity: "Simple",
  confidence: 0.92,
  reasoning: "Clear request to write specific function with basic scope"
}
```

### Stage 3: Analyzer
```
Input:  Processed prompt
Output: {
  intent: "Create Python sort function",
  requirements: ["Function", "Sort arrays", "Python"],
  context: [],
  constraints: [],
  expected_output: "Python function code",
  missing_information: ["Algorithm type", "Performance requirements"],
  ambiguities: ["Which sorting algorithm?"]
}
```

### Stage 4: Validator
```
Input:  Prompt + Analysis
Output: {
  validation: {
    clarity: { score: 7.5, level: "Good" },
    specificity: { score: 5.0, level: "Moderate" },  ← LOW
    context: { score: 7.5, level: "Good" },
    completeness: { score: 7.5, level: "Good" },
    requirements: { score: 5.0, level: "Moderate" }, ← LOW
    constraints: { score: 2.5, level: "Poor" },      ← VERY LOW
    expected_output: { score: 7.5, level: "Good" },
    actionability: { score: 7.5, level: "Good" }
  },
  overall_issues: [...],
  improvement_targets: ["specificity", "requirements", "constraints"]
}
```

### Stage 5: Scoring Engine
```
Input:  Validation scores
Output: {
  dimension_scores: { clarity: 7.5, specificity: 5.0, ... },
  overall_score: 6.31,           ← < 7.0 (needs improvement)
  threshold: 7.0,
  status: "Needs Improvement",
  low_scoring_dimensions: ["constraints", "specificity", "requirements"]
}
```

### Decision: Score 6.31 < 7.0 → IMPROVE

### Stage 6: Improver
```
Input:  Original prompt + all analysis/scores
Output: {
  improved_prompt: "Write a Python function that implements the bubble sort 
                    algorithm to sort arrays in ascending order...",
  changes_made: [
    "Specified sorting algorithm (bubble sort)",
    "Added order specification (ascending)",
    "Added edge case handling"
  ],
  dimensions_addressed: ["specificity", "constraints", "requirements"],
  intent_preserved: true,
  iteration: 1
}
```

### Re-validation (Loop back)
Validator re-run on improved prompt → scores improve  
Scoring Engine re-run → overall_score: 8.19 ≥ 7.0 → EXIT LOOP ✓

### Stage 7: Report
```
Output: {
  original_prompt: "Write a Python function that sorts arrays",
  classification: { ... },
  analysis: { ... },
  initial_evaluation: { overall_score: 6.31, ... },
  improvement_history: [ { iteration: 1, changes: [...] } ],
  final_evaluation: { overall_score: 8.19, ... },
  final_prompt: "Write a Python function that implements bubble sort...",
  summary: "Prompt improved by 1.88 points (6.31 → 8.19) over 1 iteration",
  status: "Ready",
  improvements_made: 1,
  iterations_required: 1
}
```

### Storage & Output
- Stored in database: `EvaluationResult.full_report`
- Returned to frontend via API
- Frontend displays results to user

---

## Testing Workflow

### Recommended Order

**Step 1:** Run Python test script (quick overview)
```bash
python test_agents.py
```

**Step 2:** Read AGENT_TESTING_GUIDE.md for detailed explanation

**Step 3:** Test specific agent via Django shell
```bash
python manage.py shell
# Test preprocessor, classifier, etc. individually
```

**Step 4:** Test via API endpoint
```bash
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your test prompt"}'
```

**Step 5:** Query database to verify storage
```bash
python manage.py shell
# Query EvaluationResult model
```

---

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `AGENT_TESTING_GUIDE.md` | Complete reference guide | 600+ |
| `backend/test_agents.py` | Executable test script | 350+ |
| `AGENT_TESTING_SUMMARY.md` | This file | - |

---

## Success Criteria

After using these tools, you should be able to:

✅ Test individual agents in isolation  
✅ See complete agent output structure  
✅ Understand data flow through pipeline  
✅ Compare results across methods  
✅ Trace a prompt through all 7 stages  
✅ Verify improvement loop logic  
✅ Export results for analysis  
✅ Troubleshoot any issues  

---

## Common Tasks

### Check Preprocessor Output Only
```bash
python manage.py shell
from evaluator.agents.preprocessor import PreprocessorAgent
agent = PreprocessorAgent()
result = agent.process("Your prompt")
print(result)
```

### See Full Pipeline with One Command
```bash
python test_agents.py
```

### Test Just Classification
```bash
python test_agents.py --method 2
```

### Export All Results to JSON
```bash
python test_agents.py --export
ls test_results/
# 01_preprocessor.json
# 02_classifier.json
# ... etc
```

### Test Custom Prompt
```bash
python test_agents.py --prompt "Your custom prompt here"
```

---

## Architecture Reminder

**7 Agents Process Sequentially:**

```
1. Preprocessor    → Normalize & Structure
2. Classifier      → Categorize & Assess
3. Analyzer        → Decompose & Extract
4. Validator       → Evaluate & Score
5. Scoring Engine  → Calculate Overall
6. Improver        → Rewrite if needed (loop)
7. Report Agent    → Aggregate & Format
```

**Key Threshold:** 7.0 out of 10  
**Max Improvements:** 3 iterations  
**Key Constraint:** Intent must be preserved in improvements

---

## Next Steps

1. **Read** [AGENT_TESTING_GUIDE.md](AGENT_TESTING_GUIDE.md)
2. **Run** `python test_agents.py` in backend directory
3. **Choose** your preferred testing method
4. **Test** with various prompts
5. **Compare** outputs across methods
6. **Export** results for detailed analysis

---

**Status:** ✅ Complete  
**Date:** 2026-09-10  
**Created Files:** 2 (guide + script)  
**Methods Documented:** 5  
**Agents Covered:** 7  
**Example Workflows:** 3
