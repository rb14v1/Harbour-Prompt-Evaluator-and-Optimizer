# How to Test Claude Prompts vs Your Project Improvements

**Complete instructions for testing and comparing.**

---

## 🎯 Three Testing Phases

### Phase 1️⃣: Test Claude API
Get real Claude improvements for deficient prompts

### Phase 2️⃣: Compare Dimensions  
Analyze how many of the 8 dimensions each approach covers

### Phase 3️⃣: Test Your Project
(Optional) Compare with your actual Improver agent

---

## ⚡ Phase 1: Claude Improvements (2 minutes)

**Goal:** Generate improved prompts using Claude API

### Command
```bash
cd "C:\Users\admin\AppData\Local\Temp\claude\c--Users-admin-Downloads-project-prompt-evaluator-and-optimizer\2bc7bf8a-fa1b-41d6-bd87-ba41afbba64a\scratchpad"

python test_claude_improvements.py
```

### What Happens
1. Loads 3 sample deficient prompts from dataset
2. Calls Claude API for each prompt
3. Stores results with timestamps

### Output File
**`claude_test_results_sample.json`** (6 KB)

Structure:
```json
[
  {
    "sample_id": "SAMPLE_001",
    "deficient_prompt": "Write something about data",
    "claude_improved": "Write a 2-3 page technical report...",
    "dataset_improved": "(pre-generated version)"
  },
  ...
]
```

### To Test More Samples
Edit the last lines of `test_claude_improvements.py`:

```python
if __name__ == "__main__":
    print("Testing Claude improvements on 10 sample prompts...\n")
    results = test_and_save(num_samples=10)  # Change 3 to 10, 50, etc
```

Then run again.

---

## 🔍 Phase 2: Dimension Comparison (1 second)

**Goal:** Analyze which approach covers more dimensions

### Command
```bash
python compare_improvements.py
```

### What Happens
1. Loads Claude results from Phase 1
2. Detects 8 dimensions in each prompt
3. Compares Claude vs pre-generated dataset version
4. Generates statistics

### Output File
**`comparison_with_project.json`** (2 KB)

### What to Look For

```json
{
  "summary": {
    "total_samples": 3,
    "claude_avg_dimensions": 3.67,        ← How many dimensions Claude adds
    "project_avg_dimensions": 3.33,       ← How many pre-generated version adds
    "claude_wins": 2,                     ← Claude better in 2 samples
    "project_wins": 1,                    ← Pre-gen better in 1 sample
    "ties": 0,
    "avg_similarity": 0.648,              ← 65% text similarity
    "dimension_wins": {
      "expected_output": {"claude": 3, "project": 0},
      "requirements": {"claude": 2, "project": 1},
      ...
    }
  }
}
```

### Interpreting

**Claude wins if:**
- `claude_avg_dimensions` > `project_avg_dimensions`
- Example: 3.67 vs 3.33 → Claude wins by 0.34 dimensions

**Per-dimension wins:**
- Look at `dimension_wins`
- Example: Claude wins 3/3 on "expected_output"

---

## 🚀 Phase 3: Test Your Project (5-10 minutes)

**Goal:** Compare with your actual Improver agent

### Prerequisites
1. Know where your Improver agent is located
2. Have Python path configured to your project

### Setup (One-Time)

**Step 1: Find your Improver**

Search your project for the Improver agent. Likely locations:
```
backend/evaluator/agents/improver.py
backend/improver.py
evaluator/improver.py
src/improver.py
```

**Step 2: Update test_project_improver.py**

Open the file and find this section around line 60:

```python
def test_project_improver_on_prompt(deficient_prompt):
    """
    Run your project's Improver agent on a deficient prompt.
    
    This is a TEMPLATE - you need to adjust based on your actual project structure.
    """
    
    try:
        # ADJUST THIS IMPORT based on your actual project structure
```

Replace the placeholder with your actual import. Examples:

**Example A:** If you have an `ImproverAgent` class
```python
from backend.evaluator.agents.improver import ImproverAgent
improver = ImproverAgent()
result = improver.improve(deficient_prompt)
return {
    'improved_prompt': result,
    'status': 'success'
}
```

**Example B:** If you have a pipeline function
```python
from backend.evaluator.pipeline import run_improvement
result = run_improvement(deficient_prompt)
return {
    'improved_prompt': result['improved_prompt'],
    'status': 'success'
}
```

**Example C:** If you use multiple agents
```python
from backend.evaluator.agents import Validator, Improver
validator = Validator()
improver = Improver()
analysis = validator.validate(deficient_prompt)
result = improver.improve(deficient_prompt, analysis)
return {
    'improved_prompt': result['improved_prompt'],
    'status': 'success'
}
```

**Step 3: Update PROJECT_PATH**

Near the top of the file:

```python
PROJECT_PATH = r"c:\Users\admin\Downloads\project\prompt-evaluator-and-optimizer"
```

Make sure this matches your actual project location.

### Command
```bash
python test_project_improver.py
```

### What Happens
1. Imports your project modules
2. Runs your Improver on test samples
3. Compares with Claude results
4. Saves comparison

### Output File
**`project_improver_test_results.json`** (4 KB)

Structure:
```json
[
  {
    "sample_id": "SAMPLE_001",
    "deficient_prompt": "Write something about data",
    "claude_improved": "Claude version...",
    "your_improved": "Your improver's version...",
    "status": "success"
  }
]
```

---

## 📊 Comparing All Results

After all three phases, you have three outputs:

### File 1: claude_test_results_sample.json
- Claude's real improvements
- Can be scored with your Validator

### File 2: comparison_with_project.json
- Dimension analysis
- Head-to-head comparison
- Statistical summary

### File 3: project_improver_test_results.json
- Your Improver's output
- Direct comparison with Claude

### How to Compare

**Option A: By Dimension Count**
```
Claude avg: 3.67/8
Your project avg: 3.33/8
Winner: Claude (0.34 advantage)
```

**Option B: By Text Similarity**
```
Similarity: 65%
Interpretation: Different but related approaches
```

**Option C: By Specific Dimensions**
```
Expected Output: Claude 3/3, Your project 0/3 → Claude wins
Clarity: Claude 1/3, Your project 3/3 → Your project wins
```

**Option D: With Your Validator Scoring**
```python
# Score both approaches with your Validator
claude_score = validator.score(claude_improved)
your_score = validator.score(your_improved)

print(f"Claude: {claude_score}")
print(f"Your project: {your_score}")
```

---

## 🎯 Real-World Usage Examples

### Example 1: Quick Check (5 min)
```bash
# Just test Claude
python test_claude_improvements.py
python compare_improvements.py

# Check comparison_with_project.json
# Done!
```

### Example 2: Full Comparison (15 min)
```bash
# Phase 1: Claude (3 samples)
python test_claude_improvements.py

# Phase 2: Analyze
python compare_improvements.py

# Phase 3: Your project
python test_project_improver.py

# Compare all three outputs
```

### Example 3: Scale Up (30 min)
```bash
# Edit test_claude_improvements.py
# Change: test_and_save(num_samples=50)

# Run Phase 1 (takes ~15 min)
python test_claude_improvements.py

# Phase 2: Analyze all 50
python compare_improvements.py

# Phase 3: Your project on 10 samples
# Edit test_project_improver.py
# Change: run_comparison_test(num_samples=10)

python test_project_improver.py

# Full comparison across 50 samples
```

---

## ✅ Checklist

### Before Testing
- [ ] You have ANTHROPIC_API_KEY set (for Claude API)
- [ ] You're in the scratchpad directory
- [ ] Python 3.8+ installed
- [ ] dataset_50_samples.json exists (pre-generated)

### Phase 1
- [ ] Run: `python test_claude_improvements.py`
- [ ] Output: `claude_test_results_sample.json` ✓
- [ ] Can see Claude improvements for 3 samples ✓

### Phase 2
- [ ] Run: `python compare_improvements.py`
- [ ] Output: `comparison_with_project.json` ✓
- [ ] See dimension wins printed to console ✓

### Phase 3 (Optional)
- [ ] Updated test_project_improver.py imports
- [ ] Updated PROJECT_PATH in script
- [ ] Run: `python test_project_improver.py`
- [ ] Output: `project_improver_test_results.json` ✓

### Analysis
- [ ] Review all JSON files
- [ ] Compare dimension scores
- [ ] Determine which approach is better
- [ ] Plan next steps

---

## 🔧 Troubleshooting

### Error: "No module named 'anthropic'"
```
pip install anthropic
```

### Error: "FileNotFoundError: dataset_50_samples.json"
```
The dataset was pre-generated in the scratchpad.
If missing, run: python dataset_generation.py
```

### Error: "AuthenticationError" (Claude API)
```
Ensure ANTHROPIC_API_KEY environment variable is set:
  PowerShell: $env:ANTHROPIC_API_KEY = "sk-..."
  Cmd: set ANTHROPIC_API_KEY=sk-...
```

### Error: "ModuleNotFoundError" (Phase 3)
```
1. Check PROJECT_PATH is correct
2. Verify import statements match your actual project structure
3. Test with: python -c "from your_module import Agent"
```

### Error: "JSON decode error"
```
Results file corrupted. Delete it and re-run:
  rm claude_test_results_sample.json
  python test_claude_improvements.py
```

---

## 📖 Additional Resources

For detailed information, see:
- **QUICK_START.md** — 2-minute overview
- **TESTING_GUIDE.md** — Complete guide with examples
- **detailed_comparison_report.md** — Initial analysis of all 50 samples

---

## 💡 Key Takeaways

1. **Phase 1 Tests Claude** — Shows real Claude improvements
2. **Phase 2 Analyzes** — Compares dimensions (0-8)
3. **Phase 3 Tests Your Project** — Direct comparison
4. **All in Scratchpad** — No project changes
5. **Results are JSON** — Easy to parse and analyze

---

## 🚀 Ready to Start?

Run this now:
```bash
python test_claude_improvements.py && python compare_improvements.py
```

Then check `comparison_with_project.json` for results!
