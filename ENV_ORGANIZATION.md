# Environment Files Organization

## ✅ Complete - All Changes Applied

---

## Directory Structure (After Changes)

```
prompt-evaluator-and-optimizer/
├── backend/
│   ├── .env                    ← MOVED HERE (backend config)
│   ├── .gitignore              ← CREATED (ignores .env)
│   ├── manage.py
│   ├── config/
│   ├── evaluator/
│   └── venv/
│
├── frontend/
│   ├── .env                    ← (already here - frontend config)
│   ├── .gitignore              ← (already has .env ignore)
│   ├── src/
│   ├── package.json
│   └── node_modules/
│
├── .gitignore                  ← ROOT (includes .env patterns)
├── README.md
├── CLAUDE.md
└── [other project files]
```

---

## What Changed

### ✅ Backend Configuration
- **Before:** `/.env` (root level, mixed config)
- **After:** `/backend/.env` (backend-only config)
- **Contains:**
  ```
  DEBUG=True
  DJANGO_SECRET_KEY=...
  DB_NAME=prompt_evaluator
  DB_USER=postgres
  DB_PASSWORD=postgres
  AZURE_OPENAI_API_KEY=...
  AZURE_OPENAI_ENDPOINT=...
  CORS_ALLOWED_ORIGINS=http://localhost:5173
  MAX_ITERATIONS=3
  THRESHOLD=7.0
  ```

### ✅ Frontend Configuration
- **Location:** `/frontend/.env` (unchanged)
- **Contains:**
  ```
  VITE_API_URL=http://localhost:8000/api
  VITE_API_TIMEOUT=30000
  ```

### ✅ Git Configuration
- **Root `.gitignore`** — Has `.env` patterns (6 patterns)
- **Backend `.gitignore`** — Created with `.env` patterns (6 patterns)
- **Frontend `.gitignore`** — Already had `.env` patterns (3 patterns)

---

## Benefits

✅ **Isolation** — Each service has its own config in its folder  
✅ **Security** — `.env` files ignored by git, prevents secret leaks  
✅ **Clarity** — Clear structure: what belongs where  
✅ **Deployment** — Each folder is self-contained  
✅ **Scalability** — Easy to add more services  

---

## How to Use

### Starting Backend

```powershell
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Django will automatically read backend\.env
python manage.py runserver

# Django reads these settings from backend/.env:
# - DEBUG
# - DJANGO_SECRET_KEY
# - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
# - AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
# - CORS_ALLOWED_ORIGINS
# - MAX_ITERATIONS, THRESHOLD
```

### Starting Frontend

```powershell
cd frontend

# Vite will automatically read frontend\.env
npm run dev

# Frontend reads these settings from frontend/.env:
# - VITE_API_URL (backend API address)
# - VITE_API_TIMEOUT (request timeout)
```

---

## Git Behavior

### Files NOT committed (properly ignored):
```
❌ .env                    (root - deleted anyway)
❌ backend/.env            (in .gitignore)
❌ frontend/.env           (in .gitignore)
❌ backend/.env.local      (in .gitignore)
❌ frontend/.env.local     (in .gitignore)
```

### Files CAN be committed (examples):
```
✅ .env.example            (in !.env.example exception)
✅ .gitignore              (root)
✅ backend/.gitignore      (new)
✅ frontend/.gitignore     (unchanged)
```

---

## File Changes Summary

| File | Status | Action |
|------|--------|--------|
| `.env` (root) | ❌ Deleted | Moved to `backend/.env` |
| `backend/.env` | ✅ Created | Moved from root |
| `backend/.gitignore` | ✅ Created | New file with .env patterns |
| `frontend/.env` | ✅ Unchanged | Already in correct location |
| `frontend/.gitignore` | ✅ Already has patterns | No changes needed |
| `.gitignore` (root) | ✅ Already has patterns | No changes needed |

---

## Verification Checklist

- ✅ `backend/.env` exists and readable
- ✅ `frontend/.env` exists and readable
- ✅ Root `.env` deleted
- ✅ `backend/.gitignore` created with .env patterns
- ✅ `frontend/.gitignore` has .env patterns
- ✅ Root `.gitignore` has .env patterns
- ✅ Django can read `backend/.env`
- ✅ Vite can read `frontend/.env`

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'python-dotenv'"

**Solution:** Install python-dotenv
```powershell
cd backend
pip install python-dotenv
```

Then Django will automatically load from `backend/.env`

### Issue: Backend doesn't see environment variables

**Check:**
1. Is `backend/.env` present? `Test-Path backend\.env`
2. Run from backend folder: `cd backend`
3. Check first line: `Get-Content backend\.env | Select-Object -First 1`
4. Restart Django: `python manage.py runserver`

### Issue: Frontend can't connect to API

**Check:**
1. Is `frontend/.env` present? `Test-Path frontend\.env`
2. Check API URL: `Get-Content frontend\.env | Select-String VITE_API_URL`
3. Verify backend running on :8000
4. Restart frontend: `npm run dev`

---

## Deployment

### Docker Setup

Each folder can be deployed independently:

**Backend Dockerfile:**
```dockerfile
WORKDIR /app/backend
COPY backend/.env .
RUN pip install -r requirements.txt
CMD ["python", "manage.py", "runserver"]
```

**Frontend Dockerfile:**
```dockerfile
WORKDIR /app/frontend
COPY frontend/.env .
RUN npm install
CMD ["npm", "run", "dev"]
```

### Production Environment

When deploying to production:

1. **Create** `backend/.env.production` with production values:
   ```
   DEBUG=False
   DB_HOST=prod-db.example.com
   AZURE_OPENAI_API_KEY=prod-key
   ```

2. **Create** `frontend/.env.production` with production API:
   ```
   VITE_API_URL=https://api.example.com
   ```

3. **Build frontend:**
   ```powershell
   cd frontend
   npm run build  # Uses frontend/.env for variables
   ```

---

## Git Commit Strategy

After these changes, when committing:

```bash
git status

# Should NOT show .env files
# Should show new files:
# - backend/.gitignore
# - backend/.env (ERROR - should not appear!)

# If backend/.env appears, it means .gitignore isn't working
# Fix: git rm --cached backend/.env
```

---

## Summary

✅ **Environment files now properly organized**
✅ **Backend config in `backend/.env`**
✅ **Frontend config in `frontend/.env`**
✅ **Both properly ignored by git**
✅ **Clean project root directory**
✅ **Easy to deploy each service independently**

---

## Next Steps

1. ✅ Commit these changes to git:
   ```bash
   git add backend/.env backend/.gitignore .gitignore frontend/.gitignore
   git commit -m "Organize environment files: move backend config to backend/ folder"
   ```

2. ✅ Start services from their respective folders:
   ```
   Terminal 1: cd backend && python manage.py runserver
   Terminal 2: cd frontend && npm run dev
   ```

3. ✅ Verify both services run correctly

---

**Status:** ✅ COMPLETE  
**Date:** 2026-09-10  
**Impact:** Cleaner structure, better security, easier deployment
