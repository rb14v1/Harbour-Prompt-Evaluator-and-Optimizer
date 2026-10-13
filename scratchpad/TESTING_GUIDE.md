# Testing Guide: Claude vs Your Project Improvements

Complete guide to test and compare Claude-generated improvements with your project's Improver agent.

---

## 📋 Quick Start (3 Steps)

### Step 1: Generate Claude Improvements
```bash
python test_claude_improvements.py
```
Generates: `claude_test_results_sample.json`

### Step 2: Compare With Dataset
```bash
python compare_improvements.py
```
Generates: `comparison_with_project.json`

### Step 3: Test Your Project
```bash
python test_project_improver.py
```
(Requires setup - see below)

---

## 🔧 Detailed Testing Workflow

### Phase 1: Claude Improvements Testing

**File:** `test_claude_improvements.py`

**What it does:**
- Takes deficient prompts from dataset
- Calls Claude API to generate improvements
- Stores results with metadata

**How to run:**
```bash
cd C:\Users\admin\AppData\Local\Temp\claude\c--Users-admin-Downloads-project-prompt-evaluator-and-optimizer\2bc7bf8a-fa1b-41d6-bd87-ba41afbba64a\scratchpad

python test_claude_improvements.py
```

**Output:**
- `claude_test_results_sample.json` — Real-time Claude improvements for 3 samples

**Customization:**
```python
# Test different number of samples
results = test_and_save(num_samples=10, output_file='claude_test_results_10.json')

# Test specific samples
results = test_multiple_prompts(num_samples=5, start_index=10)

# Test single prompt interactively
improved = test_single_prompt("Your vague prompt here", verbose=True)
```

**Output format:**
```json
[
  {
    "sample_id": "SAMPLE_001",
    "deficient_prompt": "Write something about data",
    "claude_improved": "Write a 2-3 page technical report on data warehousing...",
    "dataset_improved": "Pre-generated version for comparison",
    "timestamp": "2026-09-28T..."
  }
]
```

---

### Phase 2: Dimension Analysis

**File:** `compare_improvements.py`

**What it does:**
- Loads Claude test results
- Detects which 8 dimensions are present in each prompt
- Compares Claude vs pre-generated dataset versions
- Generates similarity metrics

**How to run:**
```bash
python compare_improvements.py
```

**Output:**
- `comparison_with_project.json` — Dimension-by-dimension comparison

**Output format:**
```json
{
  "summary": {
    "total_samples": 3,
    "claude_avg_dimensions": 3.67,
    "project_avg_dimensions": 3.33,
    "claude_wins": 2,
    "project_wins": 1,
    "ties": 0,
    "avg_similarity": 0.65,
    "dimension_wins": {
      "expected_output": {"claude": 3, "project": 0},
      "requirements": {"claude": 2, "project": 1},
      ...
    }
  },
  "comparisons": [...]
}
```

**Key metrics:**
- `claude_avg_dimensions` — How many of the 8 dimensions Claude adds (0-8)
- `project_avg_dimensions` — How many your project approach adds
- `similarity` — Text similarity between approaches (0-1)
- `dimension_wins` — Which approach wins per dimension

---

### Phase 3: Project Integration Testing

**File:** `test_project_improver.py`

**What it does:**
- Imports your actual project modules
- Runs your Improver agent on test samples
- Compares your results with Claude results

**How to set up:**

**Step 1: Locate your Improver agent**

Find where your Improver is defined in your project. Common paths:
```
backend/evaluator/agents/improver.py
backend/improver.py
backend/agents.py
evaluator/improver.py
```

**Step 2: Update the script**

Open `test_project_improver.py` and update the import section:

```python
# Option 1: If you have an Improver class
from backend.evaluator.agents.improver import ImproverAgent
improver = ImproverAgent()
result = improver.improve(deficient_prompt)

# Option 2: If you have a pipeline function
from backend.evaluator.pipeline import run_improvement
result = run_improvement(deficient_prompt)

# Option 3: Multiple agents
from backend.evaluator.agents import Validator, Improver
validator = Validator()
improver = Improver()
analysis = validator.validate(deficient_prompt)
result = improver.improve(deficient_prompt, analysis)
```

**Step 3: Run the test**

```bash
python test_project_improver.py
```

**Expected output:**
- `project_improver_test_results.json` — Your improvements compared to Claude

---

## 📊 Understanding Results

### Dimension Detection

The comparison script detects 8 dimensions by looking for keywords:

| Dimension | Keywords |
|-----------|----------|
| **Clarity** | clearly, specific, understand, straightforward |
| **Specificity** | exact, detailed, example, particular, include |
| **Context** | context, background, current, existing |
| **Completeness** | all, complete, entire, comprehensive |
| **Requirements** | require, must, should, need |
| **Constraints** | constraint, limit, maximum, minimum |
| **Expected Output** | output, format, return, provide, deliverable |
| **Actionability** | immediately, ready, deploy, execute, step |

### Similarity Metric

Text similarity (0-1 scale):
- `0.0` = Completely different approaches
- `0.5` = Similar structure, different wording
- `1.0` = Identical text

### Winner Determination

Prompt with more dimensions wins:
- Claude: 7/8 dimensions ✓
- Your Project: 5/8 dimensions ✗
- **Winner: Claude** (by dimension count)

---

## 🎯 Complete Testing Workflow

### Test 1: Small Sample (Quick)
```bash
# Test 3 samples
python test_claude_improvements.py

# Compare results
python compare_improvements.py

# Check comparison_with_project.json for results
```
**Time:** ~5 minutes  
**Output:** Quick dimensionality comparison

---

### Test 2: Medium Dataset (Thorough)

Edit `test_claude_improvements.py` and change:
```python
if __name__ == "__main__":
    results = test_and_save(num_samples=10)  # Change from 3 to 10
```

Run:
```bash
python test_claude_improvements.py
python compare_improvements.py
```

**Time:** ~10-15 minutes  
**Output:** More statistically significant results

---

### Test 3: Full Pipeline (Complete)

1. **Get all Claude improvements:**
```bash
# Modify to use all 50 samples
python test_claude_improvements.py  # num_samples=50
```

2. **Analyze dimensions:**
```bash
python compare_improvements.py
```

3. **Score with your Validator:**
```bash
# Create a new script using your Validator agent
# Load claude_test_results_sample.json
# Run each improvement through your Validator
# Compare scores
```

**Time:** ~30-45 minutes  
**Output:** Complete dimension + scoring comparison

---

## 🔍 Interpreting the Results

### Example Output

```
==============================================================
COMPARISON SUMMARY: Claude vs Your Project Improvements
==============================================================

Total Samples Compared: 3

Dimension Coverage:
  Claude avg:  3.67/8 dimensions
  Project avg: 3.33/8 dimensions

Heads-to-Head Results:
  Claude wins:  2
  Project wins: 1
  Ties:         0

Avg Text Similarity: 64.8%

Dimension-Specific Wins:
  CLARITY            - Claude: 1, Project: 2
  SPECIFICITY        - Claude: 2, Project: 1
  CONTEXT            - Claude: 3, Project: 0
  COMPLETENESS       - Claude: 1, Project: 2
  REQUIREMENTS       - Claude: 3, Project: 0
  CONSTRAINTS        - Claude: 2, Project: 1
  EXPECTED_OUTPUT    - Claude: 3, Project: 0
  ACTIONABILITY      - Claude: 2, Project: 1
```

**What this tells you:**
- Claude is better at: CONTEXT, REQUIREMENTS, EXPECTED_OUTPUT, ACTIONABILITY
- Your project is better at: CLARITY, COMPLETENESS
- Overall: Claude wins slightly (2 vs 1) but different approaches

---

## 🛠️ Advanced Usage

### Custom Testing Function

Create `custom_test.py`:
```python
from test_claude_improvements import get_claude_improvement
from compare_improvements import analyze_improvement

# Test specific prompts
prompts = [
    "Create a document",
    "Build an API",
    "Optimize performance"
]

for prompt in prompts:
    improved = get_claude_improvement(prompt)
    analysis = analyze_improvement(prompt, improved)
    
    print(f"Prompt: {prompt}")
    print(f"Dimensions: {analysis['claude_dimensions']}/8")
    print()
```

### Batch Testing All 50

```python
# Modify test_claude_improvements.py
results = test_and_save(num_samples=50, output_file='all_50_claude_results.json')

# Then compare
# This will take ~10-15 minutes
```

### Scoring Integration

Once you have all improvements, score them with your Validator:

```python
import json
from your_project.validators import ValidatorAgent

validator = ValidatorAgent()

with open('claude_test_results_sample.json') as f:
    results = json.load(f)

for result in results:
    claude_improved = result['claude_improved']
    score = validator.evaluate(claude_improved)
    
    result['claude_score'] = score
    result['dimensions_scoring'] = score['dimension_scores']

# Save with scores
json.dump(results, open('claude_with_scores.json', 'w'))
```

---

## 📈 What to Compare

### After Running All Tests, You'll Have:

1. **claude_test_results_sample.json**
   - Real Claude improvements
   - Can be compared with your Improver output

2. **comparison_with_project.json**
   - Dimension analysis
   - Similarity metrics
   - Head-to-head wins

3. **project_improver_test_results.json** (after setup)
   - Your Improver's output
   - Direct comparison with Claude

### Key Comparisons to Make:

| Comparison | Files | What to Check |
|-----------|-------|---------------|
| Dimension Coverage | All 3 | Which approach adds more dimensions? |
| Text Similarity | comparison_with_project.json | How different are the approaches? |
| Quality Scores | Your project scoring | Which gets higher validation scores? |
| Speed/Performance | Test runtime | Which is faster? |
| Consistency | Multiple runs | Which is more consistent? |
| Domain Relevance | Your judgment | Which fits your use case better? |

---

## 🐛 Troubleshooting

### "claudia module not found"
```
Error: ModuleNotFoundError: No module named 'anthropic'

Fix: pip install anthropic
```

### "JSON file not found"
```
Error: FileNotFoundError: [Errno 2] No such file

Make sure you ran test_claude_improvements.py first:
  python test_claude_improvements.py
```

### "Import error from project"
```
Error: ModuleNotFoundError: No module named 'backend.evaluator'

Update test_project_improver.py:
1. Check your actual import paths
2. Ensure PROJECT_PATH is correct
3. Verify module structure
```

### "API authentication error"
```
Error: AuthenticationError

Ensure ANTHROPIC_API_KEY is set:
  $env:ANTHROPIC_API_KEY = "your-key"
```

---

## 💾 File Organization

```
scratchpad/
├── TESTING_GUIDE.md                      (this file)
├── 
├── Scripts:
├── test_claude_improvements.py           (generate Claude improvements)
├── compare_improvements.py               (dimension analysis)
├── test_project_improver.py              (test your project)
├──
├── Generated Results:
├── dataset_50_samples.json               (source data - 50 samples)
├── claude_test_results_sample.json       (Claude improvements - 3 samples)
├── comparison_with_project.json          (dimension comparison)
└── project_improver_test_results.json    (your project results - after setup)
```

---

## 🎓 Next Steps

1. ✅ **Run Phase 1:** `python test_claude_improvements.py`
2. ✅ **Run Phase 2:** `python compare_improvements.py`
3. 🔄 **Set up Phase 3:** Update `test_project_improver.py` with your imports
4. ✅ **Run Phase 3:** `python test_project_improver.py`
5. 📊 **Analyze results:** Review all JSON files and compare dimensions/scores

---

## 📝 Notes

- All testing happens in scratchpad (no project changes)
- Claude testing uses your ANTHROPIC_API_KEY
- Results are saved as JSON for further analysis
- You can run tests multiple times with different parameters
- All original project files remain untouched
