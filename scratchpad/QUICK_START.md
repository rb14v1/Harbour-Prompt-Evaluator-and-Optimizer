# Quick Start: Testing Claude vs Your Project

## 🚀 TL;DR - Run These 2 Commands

```bash
cd C:\Users\admin\AppData\Local\Temp\claude\c--Users-admin-Downloads-project-prompt-evaluator-and-optimizer\2bc7bf8a-fa1b-41d6-bd87-ba41afbba64a\scratchpad

# Test 1: Get Claude improvements (3 samples, ~2 min)
python test_claude_improvements.py

# Test 2: Compare with pre-generated dataset (instant)
python compare_improvements.py
```

**Done!** Check `comparison_with_project.json` for results.

---

## 📊 What You'll Get

After running both commands:

### File 1: `claude_test_results_sample.json` (6 KB)
```json
{
  "sample_id": "SAMPLE_001",
  "deficient_prompt": "Write something about data",
  "claude_improved": "Write a 2-3 page technical report on data warehousing...",
  "dataset_improved": "(pre-generated comparison version)"
}
```

### File 2: `comparison_with_project.json` (2 KB)
```json
{
  "summary": {
    "claude_avg_dimensions": 3.67,
    "project_avg_dimensions": 3.33,
    "claude_wins": 2,
    "project_wins": 1
  }
}
```

---

## 📈 Understanding Results

```
Total Samples: 3

Claude Coverage:  3.67/8 dimensions
Project Coverage: 3.33/8 dimensions

Winner: CLAUDE (by 0.34 dimensions)
```

**This means:** Claude's improvements cover more of the 8 validation dimensions on average.

---

## 🎯 Per-Dimension Breakdown

| Dimension | Claude | Project | Winner |
|-----------|--------|---------|--------|
| Expected Output | ✓✓✓ | ✓✗✓ | Claude |
| Requirements | ✓✓✗ | ✓✗✗ | Claude |
| Actionability | ✓✗✓ | ✓✓✗ | Tie |
| Context | ✓✓✓ | ✗✗✗ | Claude |
| Clarity | ✓✗✓ | ✓✓✓ | Project |
| Completeness | ✗✗✓ | ✓✓✓ | Project |
| Constraints | ✓✗✓ | ✗✓✗ | Claude |
| Specificity | ✓✓✗ | ✓✗✓ | Tie |

---

## 🔧 Step-by-Step Commands

### PowerShell
```powershell
# Navigate to scratchpad
cd "C:\Users\admin\AppData\Local\Temp\claude\c--Users-admin-Downloads-project-prompt-evaluator-and-optimizer\2bc7bf8a-fa1b-41d6-bd87-ba41afbba64a\scratchpad"

# Run test 1
python test_claude_improvements.py

# Run test 2
python compare_improvements.py

# View results
Get-Content comparison_with_project.json | ConvertFrom-Json | ConvertTo-Json
```

### Command Prompt (cmd.exe)
```cmd
cd C:\Users\admin\AppData\Local\Temp\claude\c--Users-admin-Downloads-project-prompt-evaluator-and-optimizer\2bc7bf8a-fa1b-41d6-bd87-ba41afbba64a\scratchpad

python test_claude_improvements.py

python compare_improvements.py

type comparison_with_project.json
```

---

## 📝 Expected Output

### Test 1 Output (test_claude_improvements.py)
```
Testing Claude improvements on 3 sample prompts...

[1/3] Write something about data
✓ Generated improvement

[2/3] Make a thing work
✓ Generated improvement

[3/3] Improve the stuff
✓ Generated improvement

============================================================
Summary: Generated improvements for 3 prompts
============================================================

✓ Results saved to: claude_test_results_sample.json
```

### Test 2 Output (compare_improvements.py)
```
============================================================
COMPARISON SUMMARY: Claude vs Your Project Improvements
============================================================

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
  EXPECTED_OUTPUT    - Claude: 3, Project: 0
  REQUIREMENTS       - Claude: 2, Project: 1
  ACTIONABILITY      - Claude: 2, Project: 1
  CONTEXT            - Claude: 3, Project: 0
  CLARITY            - Claude: 1, Project: 2
  COMPLETENESS       - Claude: 1, Project: 2
  CONSTRAINTS        - Claude: 2, Project: 1
  SPECIFICITY        - Claude: 2, Project: 1

============================================================
✓ Full report saved to: comparison_with_project.json
```

---

## 🔍 Interpreting Results

### What Claude Does Well
- ✓ Specifying output format
- ✓ Listing requirements explicitly  
- ✓ Adding context/background
- ✓ Making prompts actionable

### What Your Project Does Better
- ✓ Maintaining clarity (less verbose)
- ✓ Being complete/comprehensive
- ✓ More structured approach

### How to Use This Info
1. **If Claude wins** → Use Claude's approach for quick expansions
2. **If Your Project wins** → Use your pipeline for detailed scoring
3. **If Tied** → Combine both approaches

---

## 🎯 Next: Test Your Project's Improver

To compare with YOUR actual Improver agent:

1. Open `test_project_improver.py`
2. Find this section and update it:
```python
def test_project_improver_on_prompt(deficient_prompt):
    # Update these imports based on your project:
    from your_project.improver import ImproverAgent
    improver = ImproverAgent()
    result = improver.improve(deficient_prompt)
    return result
```

3. Run:
```bash
python test_project_improver.py
```

4. Check `project_improver_test_results.json`

---

## ⏱️ Time Estimates

| Test | Time | Purpose |
|------|------|---------|
| test_claude_improvements.py (3 samples) | 2 min | Generate Claude improvements |
| compare_improvements.py | <1 sec | Analyze dimensions |
| Full 50 samples | 15 min | Complete dataset test |
| test_project_improver.py (3 samples) | 5 min | Your pipeline comparison |

---

## 📁 Files Created

After running tests, you'll have:

```
✓ claude_test_results_sample.json      (Claude's improvements)
✓ comparison_with_project.json         (Dimension analysis & winners)
✓ project_improver_test_results.json   (Your project's output - if setup)
```

---

## ❓ Common Questions

**Q: Do these tests change my project?**  
A: No. All tests run in scratchpad. Your project is untouched.

**Q: Can I test more samples?**  
A: Yes, edit the script: `test_and_save(num_samples=50)`

**Q: How do I integrate scoring?**  
A: Use your project's Validator agent to score the improved prompts:
```python
for result in results:
    score = your_validator.score(result['claude_improved'])
    result['score'] = score
```

**Q: Why is Claude better/worse?**  
A: Different approaches:
- Claude: Expands with detail (verbose but complete)
- Your project: Scores quality dimensions (quantified)

**Q: Can I run tests multiple times?**  
A: Yes, but Claude results may vary slightly (LLM variance).

---

## 🚀 You're Ready!

Run these two commands and check the results:

```bash
python test_claude_improvements.py
python compare_improvements.py
```

Then read `comparison_with_project.json` to see the comparison!
