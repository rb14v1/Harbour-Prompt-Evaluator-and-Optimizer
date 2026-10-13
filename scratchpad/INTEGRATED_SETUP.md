# 🚀 Integrated Setup Guide: Claude vs Project

Complete setup to compare Claude and your Project's prompt improvements with 8-dimension scoring and Excel export.

---

## 📋 What You'll Get

**Answer to: "How will Claude take the prompt and improvise it as in my project?"**

### The Workflow:

```
User enters prompt
    ↓
PARALLEL PROCESSING:
    ├─ CLAUDE PATH
    │  ├─ Claude receives 8-dimension improvement instructions
    │  ├─ Claude improves prompt (Clarity, Specificity, Context, etc.)
    │  ├─ Result: Improved prompt
    │  └─ Your Validator scores it on 8 dimensions
    │
    └─ PROJECT PATH
       ├─ Your Preprocessor processes prompt
       ├─ Your Analyzer breaks it down
       ├─ Your Validator scores it
       ├─ Your Improver improves it (targets low dimensions)
       ├─ Result: Improved prompt
       └─ Your Validator scores the improved version

↓
COMPARISON:
├─ Claude scores: clarity, specificity, context, completeness, requirements, constraints, expected_output, actionability
├─ Project scores: (same 8 dimensions)
└─ Excel generated with all comparisons

↓
Results shown in beautiful web UI with:
├─ Side-by-side dimension scores
├─ Overall scores
├─ Winner for each dimension
└─ Download Excel button
```

---

## 🔑 Key Point: How Claude Improves

Claude doesn't know about your project. Instead:

1. **We tell Claude** in the system prompt to improve the prompt considering **8 specific dimensions**
2. **Claude naturally improves** the prompt to address all 8 dimensions
3. **Your project also improves** using your Improver Agent
4. **Both get scored** using your ValidatorAgent
5. **We compare** the results

This way:
- ✅ Claude uses pure LLM improvement (with dimension guidance)
- ✅ Your project uses its structured pipeline
- ✅ Both are evaluated fairly on the same 8 dimensions

---

## 🛠️ Setup Steps

### Step 1: Install Dependencies

```bash
pip install flask openpyxl anthropic
```

### Step 2: Set Environment Variables

**PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxx..."
$env:AZURE_OPENAI_API_KEY = "your-azure-key"
$env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4"
$env:AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
```

**Or in `.env` file in your project:**
```
ANTHROPIC_API_KEY=sk-ant-xxxxx...
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Step 3: Run the Integrated App

```bash
cd "C:\Users\admin\AppData\Local\Temp\claude\c--Users-admin-Downloads-project-prompt-evaluator-and-optimizer\2bc7bf8a-fa1b-41d6-bd87-ba41afbba64a\scratchpad"

python app_integrated.py
```

You should see:
```
============================================================
INTEGRATED PROMPT IMPROVER
============================================================
Claude API: ✓ Available
Project Agents: ✓ Available

Open browser: http://localhost:5000
============================================================
```

### Step 4: Open in Browser

Go to: **http://localhost:5000**

---

## 📊 How It Works

### 1. User Enters Prompt

Example:
```
"Write a blog post about AI"
```

### 2. Claude Improvement (Pure LLM with Dimension Awareness)

Claude receives:
- System prompt: "Improve considering 8 dimensions: clarity, specificity, context..."
- User prompt: "Write a blog post about AI"

Claude returns:
```
"Write a 1500-word blog post about AI adoption in enterprise companies. 
Include: (1) current state of AI, (2) business benefits, (3) implementation 
challenges, (4) real-world examples. Target audience: C-level executives. 
Format: markdown with images. Deadline: 2 weeks."
```

### 3. Project Improvement (Using Your Agents)

Your pipeline:
1. Preprocessor: Normalizes text
2. Classifier: Identifies task type
3. Analyzer: Decomposes requirements
4. Validator: Scores on 8 dimensions (scores: clarity=7.5, specificity=6.0, ...)
5. Improver: Targets low dimensions and improves
6. Validator: Re-scores improved version

### 4. Scoring (Both Use Your Validator)

Both improved prompts get scored on:
- **Clarity** (2.5-10.0)
- **Specificity** (2.5-10.0)
- **Context** (2.5-10.0)
- **Completeness** (2.5-10.0)
- **Requirements** (2.5-10.0)
- **Constraints** (2.5-10.0)
- **Expected Output** (2.5-10.0)
- **Actionability** (2.5-10.0)

### 5. Comparison

Side-by-side table:
```
Dimension          | Claude | Project | Difference | Winner
Clarity            | 8.5    | 8.0     | +0.5       | Claude
Specificity        | 7.5    | 8.5     | -1.0       | Project
Context            | 8.0    | 7.5     | +0.5       | Claude
...

OVERALL SCORE      | 7.7    | 7.8     |            | Project
```

### 6. Excel Export

Download Excel with:
- Original prompt
- Both improved prompts
- All dimension scores
- Overall scores
- Winner for each dimension

---

## 🎯 File Structure

```
scratchpad/
├── app_integrated.py          (Flask backend - MAIN FILE)
├── templates/
│   └── integrated.html        (Beautiful web UI)
├── dataset_50_samples.json    (Your 50 samples)
└── INTEGRATED_SETUP.md        (This file)
```

---

## 🌐 The Web Interface

### Input Page (Main)
- Enter your prompt
- Click "Compare Improvements"
- See results instantly

### Results View
- **Scores Table** - All 8 dimensions compared
- **Overall Scores** - Claude vs Project
- **Both Improved Prompts** - Side-by-side
- **Download Excel** - Full comparison in Excel format

---

## 📈 What Gets Compared

| Aspect | Claude | Project |
|--------|--------|---------|
| Approach | Pure LLM (with dimension instructions) | Structured pipeline (Analyzer → Improver) |
| Awareness | Knows about 8 dimensions | Uses dimension-aware improver |
| Speed | Fast (1-2 seconds) | Slower (uses all agents) |
| Consistency | Can vary | More consistent |
| Scoring | Your ValidatorAgent | Your ValidatorAgent |

---

## ❓ Answers to Your Questions

### Q: How does Claude improve without knowing my project?
**A:** We give Claude explicit instructions about the 8 dimensions in the system prompt. Claude improves the prompt to maximize all 8 dimensions naturally.

### Q: How are they compared fairly?
**A:** Both improvements are scored using YOUR ValidatorAgent on the same 8 dimensions with the same scoring rules.

### Q: Which is better?
**A:** The Excel and web UI show which wins on each dimension. You can see:
- Which approach is better overall
- Which is better for each specific dimension
- By how much (the difference column)

### Q: Why use Claude if I have a project improver?
**A:** To:
1. Benchmark your improver against Claude
2. See different improvement strategies
3. Get fresh perspectives
4. Compare quality systematically

### Q: Can I customize the dimensions?
**A:** Yes! The dimensions are in `app_integrated.py` line showing `DIMENSIONS = [...]`. Edit as needed.

---

## 🔧 Troubleshooting

### "Project agents not available"
**Problem:** Can't import your agents
**Solution:**
1. Check PROJECT_PATH in app_integrated.py
2. Ensure your project structure is correct
3. Verify you're using correct import paths

### "Claude API not configured"
**Problem:** ANTHROPIC_API_KEY not set
**Solution:**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### "Azure OpenAI error"
**Problem:** Your project uses Azure but keys not set
**Solution:**
1. Set all Azure environment variables
2. Or disable Azure: `$env:DISABLE_AZURE = "true"`

### "Port 5000 already in use"
**Problem:** Another process using port 5000
**Solution:**
Change port in app_integrated.py:
```python
app.run(debug=True, port=5001)  # Use 5001 instead
```

---

## 📝 Example Workflow

1. **User enters:** "Create a system design document"

2. **Claude improves to:**
   ```
   "Create a comprehensive system design document for a scalable 
   e-commerce platform handling 1M+ users. Include: (1) architecture 
   overview, (2) database schema, (3) API design, (4) scalability 
   strategy, (5) security considerations. Format: Markdown with 
   diagrams. Target: Senior engineers. Success criteria: <2s page load."
   ```

3. **Project improves to:**
   ```
   "Create a system design document.
   
   Context: E-commerce platform for 1M+ users
   
   Requirements:
   - Scalable architecture
   - Database design
   - API specifications
   - Performance targets
   
   Constraints:
   - <2s page load time
   - High availability required
   
   Expected Output:
   - Markdown document with diagrams
   - Audience: Senior engineers
   
   Actionability:
   - Immediately deployable
   - Production-ready specifications"
   ```

4. **Scores:**
   - Claude: 7.2/10 overall
   - Project: 7.8/10 overall
   - Project wins on Completeness and Constraints
   - Claude wins on Clarity and Specificity

5. **Excel generated** with all comparisons

---

## 🚀 Ready to Go?

1. Set environment variables
2. Run: `python app_integrated.py`
3. Open: http://localhost:5000
4. Enter a prompt
5. Click "Compare Improvements"
6. See results and download Excel!

---

## 📞 Need Help?

The web UI is self-explanatory:
- Enter prompt
- Click compare
- See dimension scores
- Download Excel

All 8 dimensions from your project are used for scoring!

**Let's go!** 🎉
