# ✅ Web App Setup & Launch

Complete guide to run the Claude Prompt Improver web application.

---

## 🔧 Step 1: Install Flask

```bash
pip install flask
```

---

## 🔑 Step 2: Set API Key

Your ANTHROPIC_API_KEY wasn't set. Do this FIRST:

### PowerShell
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxx"
```

### Command Prompt (cmd)
```cmd
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

Replace `sk-ant-xxxxxxxxxxxxx` with your actual API key from https://console.anthropic.com

---

## 🚀 Step 3: Start the App

From the scratchpad directory:

```bash
python app.py
```

You should see:
```
============================================================
Starting Claude Prompt Improver
============================================================

Open browser: http://localhost:5000
============================================================
```

---

## 🌐 Step 4: Open in Browser

Click here: **http://localhost:5000**

Or copy-paste in your browser.

---

## 📍 Two Pages

### Page 1: Improve Prompt
- Enter any prompt
- Click "Improve with Claude"
- Get Claude's improved version
- Copy to clipboard

### Page 2: Compare Results
- Test 5 or 50 samples
- See Claude improvements vs Your Project improvements
- Compare side-by-side
- Check similarity %

---

## 📁 What's Running

- **app.py** — Flask backend (handles Claude API calls)
- **templates/improve.html** — Page 1 (input & improvement)
- **templates/compare.html** — Page 2 (comparison)
- **dataset_50_samples.json** — Your 50 samples (for comparison)

---

## ✨ Features

✅ **Beautiful UI** — No JSON, pure web interface  
✅ **Real-time Claude** — Pure LLM improvements (no dimensions)  
✅ **Side-by-side Comparison** — Claude vs Your Project  
✅ **Similarity Scoring** — Shows how different they are  
✅ **Copy to Clipboard** — Easy to copy results  
✅ **Responsive Design** — Works on desktop & mobile  

---

## 🛑 Stop the App

Press: **Ctrl + C** in the terminal

---

## ❓ Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```
pip install flask
```

### "ERROR: ANTHROPIC_API_KEY not set!"
```
Set the environment variable (Step 2 above)
Then restart the app
```

### "Address already in use"
```
Port 5000 is busy. Change it in app.py:
  app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### "Can't open http://localhost:5000"
```
Wait 5 seconds for Flask to start
Then try again
```

---

## 📊 What Each Page Does

### Page 1: Improve Prompt
```
Input: "Create a document"
      ↓
Claude improves it
      ↓
Output: "Create a 1500-word technical documentation..."
```

### Page 2: Compare
```
Sample from dataset
      ↓
Claude improves it
      ↓
Compare with Your Project's version
      ↓
Show: Side-by-side + Similarity %
```

---

## 🎯 Now You Can:

✅ Enter your own prompts and see Claude improve them  
✅ Compare with your project's approach  
✅ See which is better in a beautiful UI  
✅ Copy improved prompts easily  
✅ Test all 50 samples at once  

---

## 🚀 Let's Go!

1. Set API key
2. Run: `python app.py`
3. Open: http://localhost:5000
4. Start improving prompts!

Done! 🎉
