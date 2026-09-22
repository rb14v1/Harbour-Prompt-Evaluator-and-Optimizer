# 🚀 Quick Start Guide

Complete working version of the Prompt Evaluator & Optimizer with full-stack setup.

---

## What You Have

✅ **Backend (Django)** - Fully implemented REST API with 6 agents  
✅ **Frontend (React + Vite)** - Complete UI with all pages  
✅ **Database (SQLite)** - Ready to use, no config needed  
✅ **API Integration** - Frontend ↔ Backend already connected  

---

## 5-Minute Setup

### Step 1: Backend Setup (First Terminal)

```powershell
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install django djangorestframework openai azure-storage-blob python-dotenv

# Apply migrations
python manage.py migrate

# Start server
python manage.py runserver

# Expected output:
# Starting development server at http://127.0.0.1:8000/
```

### Step 2: Frontend Setup (Second Terminal)

```powershell
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev

# Expected output:
# VITE v4.4.0  ready in 123 ms
# ➜  Local:   http://localhost:5173/
```

### Step 3: Test in Browser

```
Open: http://localhost:5173
```

---

## Verify Everything Works

### Method 1: Browser Test (Easiest)

1. Go to http://localhost:5173
2. On **Home** page, enter a prompt like:  
   `"Write a Python function that sorts arrays"`
3. Click **"Evaluate Prompt"**
4. Should see results within 5-10 seconds

### Method 2: PowerShell Test

```powershell
# Run this from project root
.\test-connection.ps1
```

### Method 3: Manual API Test

```powershell
# Health check
curl http://localhost:8000/api/health/

# Submit a prompt
curl -X POST http://localhost:8000/api/evaluations/evaluate/ `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Write a Python function"}'

# View history
curl http://localhost:8000/api/history/
```

---

## Common Issues & Fixes

### Issue: "Module not found" error

**Problem:** Python packages not installed  
**Fix:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install django djangorestframework openai azure-storage-blob python-dotenv
python manage.py migrate
```

### Issue: "Address already in use" port 8000 or 5173

**Problem:** Port already running  
**Fix:**
```powershell
# Kill the process using the port
# For port 8000:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Try different port:
python manage.py runserver 8001
```

### Issue: "No module named 'evaluator'"

**Problem:** Django not finding app  
**Fix:**
```powershell
cd backend
python manage.py migrate
# Check config/settings.py has 'evaluator' in INSTALLED_APPS
```

### Issue: Blank page in browser

**Problem:** Frontend build issue  
**Fix:**
```powershell
cd frontend
rm -r node_modules dist .vite
npm install
npm run dev
```

### Issue: "Cannot fetch from API"

**Problem:** CORS or backend not running  
**Check:**
1. Backend running on http://localhost:8000/api
2. Frontend .env has correct `VITE_API_URL=http://localhost:8000/api`
3. Check browser console for errors (F12)

---

## Architecture Overview

```
┌─────────────────────────┐
│   React Frontend        │
│   http://localhost:5173 │
│  - Home page            │
│  - Results page         │
│  - History page         │
│  - About page           │
└────────────┬────────────┘
             │ Axios
             │ (HTTP calls)
             ↓
┌─────────────────────────┐
│  Django REST API        │
│  http://localhost:8000  │
│  - Evaluation engine    │
│  - History storage      │
│  - 6 AI agents          │
└────────────┬────────────┘
             │ ORM
             │
             ↓
┌─────────────────────────┐
│   SQLite Database       │
│   (auto-created)        │
│  - Prompts              │
│  - Evaluations          │
│  - Results              │
└─────────────────────────┘
```

---

## File Structure

```
prompt-evaluator-and-optimizer/
├── backend/                   # Django REST API
│   ├── manage.py             # Django command runner
│   ├── config/               # Settings & URLs
│   │   ├── settings.py       # Database, CORS, auth
│   │   └── urls.py           # API routes
│   ├── evaluator/            # Main app
│   │   ├── models.py         # Database models (7 models)
│   │   ├── views.py          # API endpoints (2 ViewSets)
│   │   ├── serializers.py    # Request/response validation
│   │   ├── orchestrator.py   # Pipeline controller
│   │   └── agents/           # 6 specialized agents
│   │       ├── preprocessor.py
│   │       ├── classifier.py
│   │       ├── analyzer.py
│   │       ├── validator.py
│   │       ├── scoring_engine.py
│   │       ├── improver.py
│   │       └── report.py
│   └── venv/                 # Virtual environment (auto-created)
│
├── frontend/                  # React + Vite
│   ├── src/
│   │   ├── pages/            # 4 page components
│   │   │   ├── Home.jsx      # Main evaluation page
│   │   │   ├── Results.jsx   # Result details
│   │   │   ├── History.jsx   # Past evaluations
│   │   │   └── About.jsx     # Project info
│   │   ├── components/       # 7 reusable components
│   │   ├── services/
│   │   │   └── api.js        # Axios client
│   │   └── App.jsx           # Routing setup
│   ├── .env                  # Configuration (VITE_API_URL)
│   ├── package.json          # Dependencies
│   └── vite.config.js        # Build config
│
├── CLAUDE.md                 # Technical architecture (850+ lines)
├── SYSTEM_PROMPT.md          # LLM system prompt for agents
├── README.md                 # User guide
└── FRONTEND_BACKEND_SETUP.md # Connection troubleshooting
```

---

## API Endpoints

### Evaluation
```
POST /api/evaluations/evaluate/
  Input: {"prompt": "your prompt text"}
  Output: Full evaluation report with scores
  Time: 5-10 seconds
```

### History
```
GET /api/history/
  Output: List of all evaluations
  
GET /api/history/{id}/
  Output: Specific evaluation details
  
GET /api/history/stats/
  Output: User statistics
```

---

## Configuration Files

### Backend (.env - optional)
```
DEBUG=True                    # Dev mode
DJANGO_SECRET_KEY=xxx        # Auto-generated
USE_POSTGRESQL=False         # Use SQLite (dev) or PostgreSQL (prod)
AZURE_OPENAI_API_KEY=xxx     # For Azure OpenAI
AZURE_OPENAI_ENDPOINT=xxx    # Azure endpoint
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

---

## Features Implemented

### Backend
✅ 6-agent orchestration pipeline  
✅ 8-dimension prompt quality validation  
✅ Iterative improvement loop (max 3 iterations)  
✅ SQLite database with 7 models  
✅ Django admin interface  
✅ RESTful API endpoints  
✅ Error handling & logging  

### Frontend
✅ React 18 + Vite  
✅ React Router navigation  
✅ Tailwind CSS styling  
✅ Dark mode toggle  
✅ Recharts visualization  
✅ Responsive design (mobile/tablet/desktop)  
✅ Loading states & error handling  
✅ Local storage (dark mode persistence)  

---

## Development Tips

### View Database (Django Admin)
```powershell
# Create superuser (first time)
python manage.py createsuperuser

# Then go to: http://localhost:8000/admin
```

### View Backend Logs
Watch the terminal running `python manage.py runserver` for:
```
[14:32:10] "POST /api/evaluations/evaluate/" 201 Created
[14:32:15] "GET /api/history/" 200 OK
```

### View Frontend Logs
- Open browser DevTools (F12)
- Go to Console tab
- Look for network requests and any errors
- Check Network tab to see API calls

### Test Individual Agents
```python
# From backend directory with venv activated
python manage.py shell

from evaluator.agents.preprocessor import PreprocessorAgent
agent = PreprocessorAgent()
result = agent.process("Your prompt here")
print(result)
```

---

## Next Steps After Setup

1. **Test the flow:**
   - Submit a prompt on Home page
   - Check Results page
   - View History page

2. **Check data:**
   - Go to http://localhost:8000/admin
   - Login with superuser credentials
   - Browse stored evaluations

3. **Try different prompts:**
   - Simple: "Sort an array"
   - Complex: "Design a system for real-time collaborative editing"
   - Edge case: "x" or empty string

4. **Monitor performance:**
   - Check how long each evaluation takes
   - Look at iteration counts
   - Review improvement suggestions

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | `pip install django djangorestframework openai` |
| Frontend won't start | `npm install` or `rm -r node_modules && npm install` |
| API connection fails | Check .env file, restart both services |
| Port 8000/5173 in use | Close other apps or use different port |
| Database locked | Delete `db.sqlite3`, re-run `python manage.py migrate` |
| CORS error | Backend already configured, restart frontend |

---

## Performance Notes

- **First evaluation:** 5-10 seconds (includes agent processing)
- **Subsequent:** Similar time (each new prompt runs full pipeline)
- **Database:** SQLite (dev) is fast enough for 100s of evaluations
- **Memory:** ~300-400MB total for both services

---

## What to Expect

### Home Page
- Prompt input form
- Feature cards explaining system
- How-it-works section

### Results Page
- Original vs improved prompts
- 8-dimension score chart
- Full evaluation details
- Improvement history (if iterations occurred)

### History Page
- Table of past evaluations
- Statistics dashboard
- Quick view links

### About Page
- Project overview
- How the system works
- Dimension explanations
- Technology stack

---

## Success Indicators

✓ Backend responds to health check  
✓ Frontend loads without errors  
✓ Can submit a prompt  
✓ Receive evaluation results  
✓ Can view history  
✓ Dark mode toggle works  
✓ No console errors  

---

## Need Help?

**Check these files:**
- [FRONTEND_BACKEND_SETUP.md](FRONTEND_BACKEND_SETUP.md) - Connection issues
- [CLAUDE.md](CLAUDE.md) - Technical architecture
- [README.md](README.md) - User guide
- [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) - Agent documentation

---

**Status:** ✅ Ready to use - all components working  
**Last Updated:** 2026-09-10  
**Framework:** Django + React + Vite  

🎉 You're all set! Start both servers and enjoy evaluating prompts!
