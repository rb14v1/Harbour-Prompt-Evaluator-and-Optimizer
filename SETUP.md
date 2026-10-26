# Prompt Evaluation & Optimization System - Complete Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- pip and npm

## Backend Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Django
DJANGO_SECRET_KEY=your-secure-secret-key-change-in-production
DJANGO_DEBUG=False  # Set to False in production

# Azure OpenAI (Recommended)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# OR OpenAI
# OPENAI_API_KEY=sk-your-api-key
# OPENAI_MODEL=gpt-4o
```

**Note**: If no API key is provided, the system automatically runs in fallback mode with intelligent deterministic generation.

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start Django Development Server

```bash
python manage.py runserver 8000
```

Backend will be available at: `http://127.0.0.1:8000/`

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment (Optional)

Create `frontend/.env.local` if you need a custom API endpoint:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 4. Start Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173/`

## Running the Application

### In Development Mode

**Terminal 1 - Backend:**
```bash
cd C:\Users\admin\Prompt
python manage.py runserver 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open `http://localhost:5173/` in your browser.

### In Production Mode

**Backend:**
```bash
# With gunicorn (install: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:8000 backend.wsgi:application

# Or with waitress (install: pip install waitress)
waitress-serve --port=8000 backend.wsgi:application
```

**Frontend:**
```bash
npm run build
# Serve the dist/ folder with a static file server
npx http-server dist/ -p 3000
```

## Testing

### Run Django Tests

```bash
python manage.py test evaluator
```

### Run with Coverage

```bash
pip install coverage
coverage run --source='evaluator' manage.py test evaluator
coverage report
coverage html  # Generate HTML report
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/evaluate/` | Evaluate prompt and generate synthetic dataset |
| GET | `/api/evaluations/` | List evaluations (supports pagination & filtering) |
| GET | `/api/evaluations/<id>/` | Get evaluation detail |
| GET | `/api/evaluations/<id>/export-excel/` | Download Excel report |
| POST | `/api/export-excel/` | Export evaluation directly to Excel |

### Example API Call

```bash
curl -X POST http://127.0.0.1:8000/api/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "department": "software",
    "task_type": "create documentation",
    "prompt": "Create JWT authentication documentation for Express.js",
    "dataset_size": 10
  }'
```

## Logging

Logs are written to:
- **Console**: Real-time output (INFO+ level)
- **File**: `logs/django.log` and `logs/evaluator_*.log` (DEBUG+ level)

Logs include:
- Request/response details
- LLM API calls and retries
- Validation errors
- Performance metrics

## Performance Optimization

### Database
- Uses SQLite by default (suitable for development)
- For production, use PostgreSQL with connection pooling:
  ```bash
  pip install psycopg2-binary
  ```

### Caching
- Enabled by default (5-minute TTL)
- Uses in-memory cache (suitable for single instance)
- For production, use Redis:
  ```bash
  pip install django-redis
  ```

### API Rate Limiting
- 60 requests per minute per IP address
- Configurable in `evaluator/middleware.py`

## Troubleshooting

### Issue: "No module named 'evaluator'"
**Solution**: Ensure you're in the correct directory and virtual environment is activated.

### Issue: "LLM API call failed"
**Solution**:
1. Check API credentials in `.env`
2. Verify API endpoint and key are correct
3. System automatically falls back to deterministic generation if API fails
4. Check logs for detailed error messages

### Issue: Database locked
**Solution**: Delete `db.sqlite3` and run migrations again:
```bash
rm db.sqlite3
python manage.py migrate
```

### Issue: Frontend can't reach backend
**Solution**:
1. Verify backend is running on port 8000
2. Check CORS settings in `backend/settings.py`
3. Update `VITE_API_BASE_URL` in frontend if needed

## Performance Benchmarks

Expected performance on standard hardware:
- Single evaluation: 3-8 seconds (varies by LLM latency)
- Synthetic dataset generation: 2-4 seconds
- Excel export: < 1 second
- Concurrent requests: 60+ requests/minute

## Database Backups

```bash
# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json
```

## Security Considerations

1. **Change SECRET_KEY**: Update `DJANGO_SECRET_KEY` in production
2. **Set DEBUG=False**: Prevents stack traces in error responses
3. **Use HTTPS**: Always use HTTPS in production
4. **API Keys**: Store API keys in environment variables, never commit to git
5. **CORS**: Restrict `CORS_ALLOW_ALL_ORIGINS` to specific domains in production
6. **Rate Limiting**: Already configured, adjust as needed
7. **Input Validation**: All requests validated with Pydantic

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests: `python manage.py test evaluator`
4. Submit pull request

## Support

For issues, check:
1. `logs/django.log` for detailed error messages
2. `logs/evaluator_*.log` for service-specific logs
3. Browser console for frontend errors
