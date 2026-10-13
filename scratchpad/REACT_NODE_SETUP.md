# 🚀 React + Node.js Setup: Claude vs Project Comparison

Complete setup guide to integrate the new comparison feature into your existing React project.

---

## 📋 What You're Getting

✅ **Node.js/Express backend** - Handles Claude comparison + Excel export  
✅ **React comparison page** - Beautiful, calm UI using your Tailwind setup  
✅ **Mock Claude responses** - Works WITHOUT API credits (swap for real API later)  
✅ **Excel generation** - Download comparison results  
✅ **Integrates with your project** - Uses your existing agents  

---

## 🛠️ Setup Instructions

### Step 1: Create Node.js Backend Folder

```bash
# In your project root
mkdir backend-nodejs
cd backend-nodejs
```

### Step 2: Copy Files

Copy these files from scratchpad to `backend-nodejs/`:

```
scratchpad/node_backend.js  →  backend-nodejs/node_backend.js
scratchpad/package_nodejs.json  →  backend-nodejs/package.json
```

### Step 3: Install Dependencies

```bash
cd backend-nodejs
npm install
```

### Step 4: Create .env (Optional)

For future real Claude API:

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
DJANGO_BACKEND_URL=http://localhost:8000/api
```

### Step 5: Add React Component

Copy the React component to your frontend:

```
scratchpad/ComparePrompts.jsx  →  frontend/src/pages/ComparePrompts.jsx
```

### Step 6: Update Frontend Router

In your `frontend/src/App.jsx`, add the new route:

```jsx
import ComparePrompts from './pages/ComparePrompts'

// In your Routes:
<Route path="/compare" element={<ComparePrompts />} />
```

### Step 7: Update Header Navigation (Optional)

Add a link to the comparison page in your `frontend/src/components/Header.jsx`:

```jsx
<a href="/compare" className="nav-link">Compare Prompts</a>
```

---

## 🚀 Running Everything

### Terminal 1: Start Node.js Backend

```bash
cd backend-nodejs
npm start
```

Expected output:
```
============================================================
Node.js Backend - Claude vs Project Comparison
============================================================
Server running on: http://localhost:3001

Endpoints:
  POST /api/compare-prompt  - Compare Claude vs Project
  POST /api/download-excel  - Download Excel file
  GET  /health             - Health check

⚠️  NOTE: Using MOCK Claude responses (no API credits needed)
    To use real Claude: Add ANTHROPIC_API_KEY to .env
============================================================
```

### Terminal 2: Start Your React Frontend

```bash
cd frontend
npm run dev
```

Your app will run on `http://localhost:5173` (Vite default)

### Terminal 3 (Optional): Start Django Backend

```bash
cd backend
python manage.py runserver
```

---

## 🎯 How It Works

### Workflow

```
User enters prompt in React UI (/compare)
    ↓
Sends to Node.js backend (localhost:3001)
    ↓
PARALLEL:
  ├─ Claude improvement (MOCK - no API key needed)
  └─ Project improvement (calls Django if available)
    ↓
Both scored on 8 dimensions
    ↓
Results shown in beautiful React UI
    ↓
User can download as Excel
```

### Architecture

```
Frontend (React/Vite)
├── localhost:5173
├── New page: /compare
└── Calls: localhost:3001/api/compare-prompt

Backend (Node.js/Express)
├── localhost:3001
├── Mock Claude improvements
├── Calls Django if available
└── Generates Excel

Django Backend
├── localhost:8000
├── Your Validator Agent
├── Your Improver Agent
└── Scoring Engine
```

---

## 🎨 UI Design

Simple, calm, effective design:

- ✅ Clean white/dark background
- ✅ Large text input area
- ✅ Minimal buttons
- ✅ Clear results table
- ✅ No clutter
- ✅ Responsive (mobile-friendly)
- ✅ Uses your Tailwind CSS

### Features

- Side-by-side comparison
- Dimension scores highlighted by color
- Winner indicator per dimension
- Overall scores
- Both improved prompts shown
- Download Excel button
- Smooth transitions

---

## 🔄 Using Real Claude API (Later)

When you add Claude API credits:

1. Add to `backend-nodejs/.env`:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

2. Update `node_backend.js` to call real Claude:
```javascript
// Replace this:
const claudeImproved = MOCK_CLAUDE_IMPROVEMENTS[prompt] || ...

// With this:
const response = await client.messages.create({
  model: "claude-opus-5-5",
  messages: [{ role: "user", content: prompt }]
})
const claudeImproved = response.content[0].text
```

3. Restart the Node backend

That's it! It will use real Claude instead of mock.

---

## 📁 File Structure After Setup

```
Your Project
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Results.jsx
│   │   │   ├── History.jsx
│   │   │   ├── About.jsx
│   │   │   └── ComparePrompts.jsx  ← NEW
│   │   ├── App.jsx  (updated with new route)
│   │   └── ...
│   └── package.json
│
├── backend/  (Django - untouched)
├── backend-nodejs/  ← NEW
│   ├── node_backend.js
│   ├── package.json
│   ├── .env (optional)
│   └── node_modules/
│
└── .env (your existing one)
```

---

## ✅ Checklist

- [ ] Created `backend-nodejs/` folder
- [ ] Copied `node_backend.js` to `backend-nodejs/`
- [ ] Renamed `package_nodejs.json` to `package.json`
- [ ] Ran `npm install` in `backend-nodejs/`
- [ ] Copied `ComparePrompts.jsx` to `frontend/src/pages/`
- [ ] Updated `App.jsx` with new route
- [ ] (Optional) Updated Header with navigation link
- [ ] Started Node backend on port 3001
- [ ] Started React frontend on port 5173
- [ ] Tested: Go to http://localhost:5173/compare

---

## 🚦 Verification

### Test Node Backend

```bash
curl http://localhost:3001/health
# Should return: {"status":"ok","server":"Node.js backend running"}
```

### Test Frontend

Go to: http://localhost:5173/compare

You should see:
- Input textarea for prompt
- "Compare Improvements" button
- Info cards explaining Claude path vs Project path

---

## 🐛 Troubleshooting

### "Cannot GET /compare"

**Problem:** React route not added  
**Solution:** Update `frontend/src/App.jsx` with the ComparePrompts route

### "Failed to connect to http://localhost:3001"

**Problem:** Node backend not running  
**Solution:** Run `npm start` in `backend-nodejs/` folder

### Module not found errors

**Problem:** Dependencies not installed  
**Solution:** Run `npm install` in both `frontend/` and `backend-nodejs/`

### "Django backend unavailable"

**Problem:** Your Django backend isn't running  
**Solution:** It's OK - Node backend will use mock responses. Start Django with `python manage.py runserver` to use real project improvements.

---

## 🎯 Features to Customize

### Change Mock Responses

In `backend-nodejs/node_backend.js`, update `MOCK_CLAUDE_IMPROVEMENTS`:

```javascript
const MOCK_CLAUDE_IMPROVEMENTS = {
  'Your prompt': 'Your improved version...'
}
```

### Change Colors

In `frontend/src/pages/ComparePrompts.jsx`, update Tailwind classes:

```jsx
className="bg-blue-600"  // Change blue to your preferred color
```

### Change Scoring Logic

In `node_backend.js`, update `mockScorePrompt()` function

---

## 📊 Example Workflow

1. Go to http://localhost:5173/compare
2. Enter: "Write a blog post"
3. Click "Compare Improvements"
4. See results:
   - Claude improved version
   - Project improved version
   - 8 dimension scores for both
   - Overall scores
5. Click "Download Excel" to save results

---

## 🔐 Security Notes

- Node backend runs on `localhost:3001` (local only)
- React communicates via `http://localhost:3001/api`
- No credentials sent to frontend
- .env file stays on server only

---

## 🚀 Next Steps

1. Follow setup steps above
2. Test the comparison feature
3. Customize UI/colors as needed
4. Add Claude API credits when ready
5. Update `node_backend.js` to use real Claude
6. Deploy when ready

---

## 📞 Questions?

- Node backend issues? Check logs in terminal
- React issues? Check browser console (F12)
- Django integration? Make sure Django is running on port 8000

All set! Start with the setup instructions above. 🎉
