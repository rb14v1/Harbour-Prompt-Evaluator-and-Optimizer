# Complete Testing Flow Guide

All fixes are complete. Follow this guide to test the entire system end-to-end.

---

## What Was Fixed

### ✅ Backend Authentication
- Temporarily disabled for testing
- Anonymous users can now submit prompts
- Production: Will be re-enabled with proper auth flow

### ✅ Backend Data Structure
- PromptHistoryViewSet now returns EvaluationResult objects
- Endpoints return correct nested data (initial_evaluation, final_evaluation)
- Serializer extracts evaluation data from JSON for frontend access

### ✅ Frontend Data Access
- History component fixed to access flat data structure
- Results component can access nested evaluation scores
- API client configured for session authentication

---

## Setup (One-Time Only)

### Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install django djangorestframework openai azure-storage-blob python-dotenv

# Run migrations
python manage.py migrate

# Create superuser (optional, for /admin)
# python manage.py createsuperuser

# Start server
python manage.py runserver

# Expected: Starting development server at http://127.0.0.1:8000/
```

### Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Verify .env exists and has:
# VITE_API_URL=http://localhost:8000/api
# VITE_API_TIMEOUT=30000

# Start dev server
npm run dev

# Expected: ➜  Local: http://localhost:5173/
```

---

## Test Plan

### Phase 1: Backend Health (2 min)

**Terminal 1:** Backend running  
**Terminal 2:** Run this

```powershell
# Health check
curl http://localhost:8000/api/health/

# Expected output:
# {"status":"ok"}
```

If failed: Backend not running. Start it first.

---

### Phase 2: Evaluate Prompt (3 min)

**Via API (Terminal 3):**

```powershell
curl -X POST http://localhost:8000/api/evaluations/evaluate/ `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Write a Python function that sorts arrays using bubble sort and explain the time complexity"}'
```

**Expected response:**
```json
{
  "original_prompt": "...",
  "classification": {
    "task_type": "create_code",
    "complexity": "Moderate",
    "confidence": 0.95,
    "reasoning": "..."
  },
  "analysis": {
    "intent": "...",
    "requirements": [...],
    "context": [...],
    "constraints": [...]
  },
  "initial_evaluation": {
    "overall_score": 6.5,
    "dimension_scores": {...}
  },
  "final_evaluation": {
    "overall_score": 8.2,
    "dimension_scores": {...}
  },
  "final_prompt": "...",
  "improvements_made": 1,
  "iterations_required": 1,
  "status": "ready",
  "summary": "Prompt improved...",
  "improvement_history": [...]
}
```

If failed:
- Check backend console for errors
- Check terminal 3 for response
- If timeout: evaluation took too long, wait for it

---

### Phase 3: View History (2 min)

**Via API (Terminal 3):**

```powershell
# Get all evaluations
curl http://localhost:8000/api/history/

# Expected: Array of evaluations with scores
# [
#   {
#     "id": "uuid",
#     "final_score": 8.2,
#     "status": "ready",
#     "original_prompt": "...",
#     "created_at": "2026-09-10T..."
#   }
# ]
```

If failed:
- Check API is working (did phase 2 work?)
- Check backend console for errors

---

### Phase 4: Frontend - Home Page (2 min)

**Browser:**
1. Open http://localhost:5173
2. Should show home page with:
   - Hero section ("Prompt Evaluator & Optimizer")
   - Input form
   - Feature cards
   - How-it-works section
   - About section

**Check:**
- [ ] Page loads without errors
- [ ] No console errors (F12 → Console)
- [ ] Dark mode toggle works (top-right)
- [ ] Navigation works (About link)

If failed:
- F12 → Console for errors
- Check .env file
- Restart frontend: `npm run dev`

---

### Phase 5: Frontend - Evaluate (5 min)

**Browser (Home page):**
1. Enter prompt:
   ```
   "Write a Python function to reverse a string"
   ```
2. Click "Evaluate Prompt" button
3. Should show loading spinner
4. After 5-10 seconds: Results page appears

**Check:**
- [ ] Loading spinner shows
- [ ] No console errors during evaluation
- [ ] Results page displays with:
   - Original prompt
   - Final score (green badge)
   - Status (Ready or Needs Review)
   - 8-dimension chart
   - Score comparison

If failed:
- Check browser console (F12 → Console)
- Check Network tab for API calls
- Check backend console for errors
- Verify API URL in .env: `VITE_API_URL=http://localhost:8000/api`

---

### Phase 6: Frontend - View Results (2 min)

**Browser (Results page):**
Already there from Phase 5. Check:
- [ ] Original prompt displayed
- [ ] Final prompt displayed (if improved)
- [ ] Initial and final scores shown
- [ ] Dimension chart shows 8 dimensions
- [ ] Improvement history (if iterations occurred)
- [ ] Status badge shows correctly

If failed:
- Check console for errors
- Verify data is coming from API (Network tab)
- Check if initial_evaluation data exists

---

### Phase 7: Frontend - History (2 min)

**Browser Navigation:**
1. Click "History" in top menu
2. Should show:
   - Statistics dashboard (4 cards)
   - Table of evaluations
   - Each row with score and status

**Check:**
- [ ] History page loads
- [ ] Stats show correct numbers
- [ ] Table displays evaluations
- [ ] Scores and status visible
- [ ] Click eye icon to view result
- [ ] Back to original evaluation

If failed:
- Check console for errors
- Verify History component is getting data
- Check if scores are displaying

---

### Phase 8: Frontend - Dark Mode (1 min)

**Browser:**
1. Click moon icon in header (top-right)
2. Page should turn dark
3. Click again to toggle back

**Check:**
- [ ] Dark mode applies to all pages
- [ ] Text remains readable
- [ ] Colors are consistent
- [ ] Setting persists on refresh

If failed:
- Check localStorage in DevTools (F12 → Application)
- Check CSS classes (should have `dark:` prefixes)

---

### Phase 9: Try Edge Cases (3 min)

**Test 1: Empty prompt**
```
Browser: Enter empty string → Click Evaluate
Expected: Error message shows
```

**Test 2: Single word**
```
Browser: Enter "Sort" → Click Evaluate
Expected: Still evaluates successfully
```

**Test 3: Very long prompt**
```
Browser: Enter 500+ character prompt → Click Evaluate
Expected: Takes longer but succeeds
```

---

## Success Criteria Checklist

### Backend
- [ ] Server starts without errors
- [ ] `/api/health/` returns OK
- [ ] `/api/evaluations/evaluate/` accepts POST
- [ ] `/api/history/` returns list
- [ ] Response includes initial_evaluation and final_evaluation
- [ ] Scores calculated correctly (0-10 scale)

### Frontend
- [ ] App loads at http://localhost:5173
- [ ] No console errors on load
- [ ] Form submits successfully
- [ ] Results page displays
- [ ] History page shows evaluations
- [ ] Dark mode works
- [ ] All links navigate correctly

### Integration
- [ ] Frontend → Backend communication works
- [ ] API calls visible in Network tab
- [ ] Evaluation completes in 5-10 seconds
- [ ] Scores match between pages
- [ ] Data persists after refresh

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Cannot GET /api/health/" | Backend not running | Start: `python manage.py runserver` |
| Blank page in browser | Frontend build error | Kill process, `npm install`, `npm run dev` |
| "Cannot fetch from API" | CORS or URL wrong | Check .env, restart both services |
| Long evaluation (>30s) | Processing slow | Normal for first run, Azure API latency |
| Empty history table | No evaluations yet | Create one first on Home page |
| Dark mode not persistent | localStorage issue | Check browser storage settings |
| API 401 error | Authentication required | Use current version (auth disabled) |

---

## Performance Expectations

| Metric | Expected |
|--------|----------|
| Health check | < 100ms |
| Single evaluation | 5-10 seconds |
| History load | < 500ms |
| Page navigation | < 100ms |
| Results chart render | < 200ms |
| Dark mode toggle | Instant |

---

## Common Response Structures

### Evaluate Response
```json
{
  "original_prompt": "string",
  "classification": {
    "task_type": "string",
    "complexity": "string",
    "confidence": 0.0-1.0
  },
  "initial_evaluation": {
    "overall_score": 0.0-10.0,
    "dimension_scores": { "clarity": 7.5, ... }
  },
  "final_evaluation": {
    "overall_score": 0.0-10.0,
    "dimension_scores": { ... }
  },
  "final_score": 0.0-10.0,
  "status": "ready" | "needs_manual_review",
  "improvements_made": 0-3,
  "iterations_required": 0-3
}
```

### History Response
```json
[
  {
    "id": "uuid",
    "original_prompt": "string",
    "final_prompt": "string",
    "final_score": 0.0-10.0,
    "status": "ready" | "needs_manual_review",
    "created_at": "ISO datetime"
  }
]
```

---

## Monitoring During Test

### Backend Console
Watch for:
```
[timestamp] "POST /api/evaluations/evaluate/" 201 Created
[timestamp] "GET /api/history/" 200 OK
```

### Frontend Console (F12)
Should see:
```
No red errors
API calls in Network tab
Evaluations completing
```

### Expected Logs
```
Backend: Processing prompt...
Backend: Running agent pipeline...
Backend: Storing result...
Backend: Returning 201 Created
Frontend: Fetching results
Frontend: Rendering page
```

---

## Final Verification

Run this PowerShell script:
```powershell
.\test-connection.ps1
```

Should show:
```
✓ Backend is running
✓ Evaluation endpoint works
✓ History endpoint works
✓ Frontend .env file exists
```

---

## Next Steps After Testing

1. **Verify all tests pass** ✓
2. **Check data in admin:**
   - Go to http://localhost:8000/admin
   - Login with superuser (if created)
   - Browse: Prompts, Evaluations, Results

3. **Try different prompts:**
   - Simple: "Sort an array"
   - Complex: "Design a cloud architecture"
   - Edge: Empty string, single word

4. **Monitor performance:**
   - Check evaluation time
   - Note iteration counts
   - Review improvement suggestions

5. **Review improvements:**
   - Check if low scores trigger improvements
   - Verify high scores skip improvement loop
   - Review suggested changes

---

## Production Checklist

When ready to deploy:
- [ ] Re-enable authentication (permission_classes = [IsAuthenticated])
- [ ] Set up proper login flow in frontend
- [ ] Configure PostgreSQL database
- [ ] Set secure DJANGO_SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure CORS for production domain
- [ ] Set DEBUG=False
- [ ] Add error logging
- [ ] Create admin user
- [ ] Backup database strategy

---

## Support

**If tests fail:**
1. Check the specific error message
2. Look it up in Troubleshooting section above
3. Check backend/frontend console for details
4. Verify both services are running
5. Try restarting both services

**Key files to check:**
- backend/evaluator/views.py - API endpoints
- frontend/src/services/api.js - API client
- frontend/.env - Configuration
- backend/evaluator/serializers.py - Data format

---

**Status:** ✅ All systems fixed and ready to test  
**Last Updated:** 2026-09-10  
**Framework:** Django REST + React + Vite  

🚀 Ready to launch testing!
