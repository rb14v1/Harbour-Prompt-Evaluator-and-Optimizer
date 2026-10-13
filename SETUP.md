# Project Setup Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip / virtualenv

## Backend Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `DJANGO_SECRET_KEY` – Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `AZURE_OPENAI_API_KEY` – Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` – Your Azure OpenAI endpoint
- Database credentials (PostgreSQL)
- Azure Storage connection string (optional)

### 4. Create PostgreSQL Database

```bash
# Using psql
psql -U postgres
CREATE DATABASE prompt_evaluator;
```

Or configure connection in `.env`:
```
DB_NAME=prompt_evaluator
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run Migrations

```bash
cd backend
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
cd backend
python manage.py createsuperuser
```

### 7. Start Development Server

```bash
cd backend
python manage.py runserver
```

Server runs at: `http://localhost:8000`
Admin panel: `http://localhost:8000/admin`

## API Endpoints

### Evaluate Single Prompt

**POST** `/api/evaluations/evaluate/`

Request:
```json
{
  "prompt": "Your prompt text here"
}
```

Response:
```json
{
  "prompt_id": "uuid",
  "original_prompt": "...",
  "classification": {...},
  "analysis": {...},
  "initial_evaluation": {...},
  "improvement_history": [...],
  "final_evaluation": {...},
  "final_prompt": "...",
  "summary": "...",
  "status": "Ready",
  "improvements_made": 1,
  "iterations_required": 1,
  "timestamp": "2026-09-09T..."
}
```

### Batch Evaluate

**POST** `/api/evaluations/batch_evaluate/`

Request:
```json
{
  "prompts": [
    "prompt 1",
    "prompt 2",
    "prompt 3"
  ]
}
```

### View History

**GET** `/api/history/`

Returns list of all prompts evaluated by current user.

### View Statistics

**GET** `/api/history/stats/`

Returns:
```json
{
  "total_prompts": 10,
  "total_evaluations": 10,
  "average_score": 7.5,
  "prompts_ready": 8,
  "prompts_needing_review": 2
}
```

## Frontend Setup (React + Vite)

### 1. Create React App

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

### 2. Install Dependencies

```bash
npm install axios react-router-dom zustand
```

### 3. Configure API URL

Create `.env`:
```
VITE_API_URL=http://localhost:8000/api
```

### 4. Start Dev Server

```bash
npm run dev
```

Frontend runs at: `http://localhost:5173`

## Testing

### Run Tests

```bash
cd backend
python manage.py test
```

### Run with Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Database Management

### Create New Migration

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Reset Database

```bash
cd backend
python manage.py migrate zero evaluator
python manage.py migrate
```

### Export Data

```bash
cd backend
python manage.py dumpdata > backup.json
```

### Import Data

```bash
cd backend
python manage.py loaddata backup.json
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` for production domain
- [ ] Set up PostgreSQL on production server
- [ ] Configure Azure OpenAI credentials
- [ ] Set up Azure Storage if needed
- [ ] Run migrations on production
- [ ] Collect static files: `python manage.py collectstatic --no-input`
- [ ] Use production-grade WSGI server (Gunicorn)
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for production frontend URL

### Deploy with Gunicorn

```bash
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

## Troubleshooting

### Database Connection Error

```
psycopg2.OperationalError: could not connect to server
```

Solution:
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists: `createdb prompt_evaluator`

### Azure OpenAI Error

```
AuthenticationError: Invalid credentials
```

Solution:
- Verify `AZURE_OPENAI_API_KEY` is correct
- Check `AZURE_OPENAI_ENDPOINT` format (should end with `/`)
- Ensure Azure OpenAI resource is deployed

### CORS Error

```
Access to XMLHttpRequest blocked by CORS policy
```

Solution:
- Add frontend URL to `CORS_ALLOWED_ORIGINS` in `.env`
- Restart backend server

### Port Already in Use

Backend:
```bash
python manage.py runserver 8001  # Use different port
```

Frontend:
```bash
npm run dev -- --port 5174  # Use different port
```

## Quick Start (Development)

```bash
# Terminal 1: Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
cd backend
python manage.py migrate
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in browser.

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Azure OpenAI API Reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## Support

For issues, check:
1. [CLAUDE.md](CLAUDE.md) – Technical architecture
2. [README.md](README.md) – Project overview
3. Backend logs: `backend/logs/`
4. Frontend console: Browser DevTools
