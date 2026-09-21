# Frontend + Backend Connection Guide

## Issues Fixed

✅ **Authentication:** Temporarily disabled for testing (marked for production implementation)  
✅ **API Client:** Added credentials support for session authentication  
✅ **Data Structure:** Backend now returns EvaluationResult objects from /history/  
✅ **Frontend:** History component fixed to access correct data fields  

---

## Quick Start (Both Services)

### Terminal 1: Backend Setup

```bash
cd backend

# Activate virtual environment
..\venv\Scripts\Activate.ps1

# Start Django server
python manage.py runserver

# Should show:
# Starting development server at http://127.0.0.1:8000/
```

### Terminal 2: Frontend Setup

```bash
cd frontend

# Start Vite dev server
npm run dev

# Should show:
# VITE v4.4.0  ready in XXX ms
# ➜  Local:   http://localhost:5173/
```

### Terminal 3: Test the Connection

```bash
# Test backend health
curl http://localhost:8000/api/health/

# Should return:
# {"status": "ok"}
```

---

## Architecture

```
Frontend (React + Vite)           Backend (Django)
localhost:5173              →     localhost:8000/api
┌─────────────────────┐           ┌─────────────────────┐
│ React App           │           │ Django REST API     │
│ - Home page         │           │ - /evaluations/     │
│ - Results page      │           │ - /history/         │
│ - History page      │           │ - /agents/          │
│ - About page        │           │ - Database (SQLite) │
└─────────────────────┘           └─────────────────────┘
       Axios                    Django REST Framework
       (http calls)
```

---

## API Endpoints

| Method | Endpoint | Purpose | Frontend Usage |
|--------|----------|---------|----------------|
| POST | `/api/evaluations/evaluate/` | Evaluate prompt | Home page form submit |
| GET | `/api/history/` | Get evaluation history | History page load |
| GET | `/api/history/{id}/` | Get specific evaluation | Results page detail |
| GET | `/api/history/stats/` | Get user statistics | History page stats |

---

## Environment Configuration

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

### Backend (.env)
```
DEBUG=True
DJANGO_SECRET_KEY=<generated>
DB_NAME=db.sqlite3
```

---

## Testing the Connection

### Method 1: Browser (Recommended)

1. Open http://localhost:5173
2. Click "Home" tab
3. Enter a prompt in the form
4. Click "Evaluate Prompt"
5. Should see results

### Method 2: Console Check

Open browser DevTools (F12) → Console tab:

```javascript
// Should show no errors
// Check Network tab for API calls
```

### Method 3: API Test

```bash
# From any terminal
curl -X POST http://localhost:8000/api/evaluations/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a function that sorts arrays"}'

# Should return evaluation results
```

---

## Troubleshooting

### Issue: "Cannot GET /api/health/"

**Problem:** Backend not running  
**Fix:**
```bash
cd backend
python manage.py runserver
```

### Issue: "Failed to fetch" in frontend

**Problem:** API URL mismatch  
**Check:**
1. Frontend .env has correct API_URL
2. Backend is running on port 8000
3. CORS is enabled in backend (it should be)

**Fix:**
```bash
# Restart frontend after .env change
npm run dev
```

### Issue: "CORS error" in browser console

**Problem:** Backend blocking frontend origin  
**Fix:** Backend has CORS enabled for localhost:5173 by default

### Issue: White/blank page

**Problem:** Frontend build error  
**Fix:**
```bash
cd frontend
rm -r node_modules dist
npm install
npm run dev
```

---

## Key Changes Made

### 1. Backend Authentication (views.py)
- ✅ Temporarily disabled `IsAuthenticated` for testing
- ✅ Changed PromptHistoryViewSet to return EvaluationResult objects
- ✅ Updated get_queryset() to handle unauthenticated users

### 2. Frontend API Client (src/services/api.js)
- ✅ Added `withCredentials: true` for session auth
- ✅ Kept error handling and interceptors

### 3. Frontend History Page (src/pages/History.jsx)
- ✅ Fixed data field access (removed `.evaluation?.`)
- ✅ Access `item.final_score` and `item.status` directly
- ✅ Component now works with EvaluationResult data

---

## Development vs Production

### Current State (Development)
- ✅ Authentication disabled for easy testing
- ✅ All endpoints accessible without login
- ✅ CORS allows localhost:5173
- ✅ SQLite database (no setup needed)

### Production Setup Needed
- [ ] Enable authentication (`permission_classes = [IsAuthenticated]`)
- [ ] Create login/auth flow in frontend
- [ ] Configure CORS for production domain
- [ ] Use PostgreSQL database
- [ ] Add environment-based settings
- [ ] Set up HTTPS

---

## Running Both Services

```bash
# Quick setup script (run once)
# Terminal 1:
cd backend && ..\venv\Scripts\Activate.ps1 && python manage.py runserver

# Terminal 2:
cd frontend && npm run dev

# Then open browser to http://localhost:5173
```

---

## Monitoring

### Backend Logs
Watch terminal 1 for:
```
[timestamp] "GET /api/history/" 200
[timestamp] "POST /api/evaluations/evaluate/" 201
```

### Frontend Logs
Watch browser DevTools → Console for:
- Network requests (Network tab)
- Any JavaScript errors
- Component rendering

---

## Success Criteria

- [ ] Frontend loads without errors
- [ ] Backend API responds to health check
- [ ] Can submit prompt for evaluation
- [ ] Can view evaluation results
- [ ] Can view evaluation history
- [ ] Dark mode toggle works
- [ ] No CORS errors in console

---

## Next Steps

1. **Start both services** using commands above
2. **Test the flow**: Home → Form → Results → History
3. **Check browser console** for any errors
4. **Check backend terminal** for API responses
5. **Report any issues** with specific error messages

---

**Status:** ✅ Fixed and Ready for Testing
