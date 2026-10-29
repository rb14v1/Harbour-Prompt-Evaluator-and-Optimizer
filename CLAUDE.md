# CLAUDE.md - Codebase Documentation

## Project Overview

**Prompt Evaluation & Optimization System** - An enterprise-grade full-stack application that:
- Evaluates prompts across 15 standardized quality dimensions (0-10 scale)
- Generates prompt-specific synthetic test datasets with balanced difficulty distribution
- Automatically optimizes prompts while preserving user intent
- Re-evaluates improvements and exports comprehensive Excel reports

**Tech Stack**: Python 3.9+ (Django 4.2, DRF) + React 19 (Vite) + SQLite (PostgreSQL ready)

**Status**: Production-ready with comprehensive error handling, logging, validation, and documentation

---

## Directory Structure

```
C:\Users\admin\Prompt/
├── backend/                          # Django configuration
│   ├── settings.py                  # Core settings with logging, caching, middleware
│   ├── urls.py                      # Main URL routes
│   ├── wsgi.py / asgi.py           # WSGI/ASGI entry points
│   └── __init__.py
│
├── evaluator/                        # Main Django app
│   ├── models.py                    # 3 models: PromptEvaluation, SyntheticDataset, SyntheticTestCase
│   ├── views.py                     # 5 API views with Pydantic validation
│   ├── serializers.py               # DRF serializers
│   ├── urls.py                      # App URL routes
│   ├── schemas.py                   # Pydantic validation schemas (NEW)
│   ├── exceptions.py                # Custom exception hierarchy (NEW)
│   ├── logging_config.py            # Logging setup (NEW)
│   ├── middleware.py                # Rate limiting & request logging (NEW)
│   ├── api_utils.py                 # Pagination & filtering utilities (NEW)
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   ├── migrations/
│   └── services/                    # Core business logic
│       ├── __init__.py
│       ├── langgraph_workflow.py   # 9-node LangGraph pipeline
│       ├── llm_client.py           # LLM API client with retries
│       ├── preprocessor.py         # Text normalization
│       ├── analyzer.py             # Semantic extraction (15+ fields)
│       ├── evaluator.py            # 15-dimension scoring
│       ├── dataset_generator.py    # Synthetic test case creation
│       ├── dataset_validator.py    # Quality checking & repair
│       ├── improver.py             # Prompt optimization
│       ├── revalidator.py          # Independent re-evaluation
│       ├── scorer.py               # Metrics & comparisons
│       └── excel_exporter.py       # Multi-tab Excel generation
│
├── frontend/                         # React 19 + Vite
│   ├── src/
│   │   ├── App.jsx                 # Main app shell with state management
│   │   ├── main.jsx                # Vite entry point
│   │   ├── App.css                 # Global styles with CSS variables
│   │   └── components/             # 8 React components
│   │       ├── Header.jsx
│   │       ├── EvaluationForm.jsx
│   │       ├── SummaryCards.jsx
│   │       ├── DimensionsTable.jsx
│   │       ├── SyntheticDatasetView.jsx
│   │       ├── PromptComparison.jsx
│   │       ├── PromptAnalysisView.jsx
│   │       └── HistoryModal.jsx
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── package-lock.json
│
├── logs/                             # Auto-created at runtime
│   ├── django.log
│   └── evaluator_*.log
│
├── db.sqlite3                        # SQLite database (development)
├── manage.py                         # Django CLI
├── requirements.txt                  # Python dependencies
│
├── README.md                         # Project overview (original)
├── SETUP.md                          # Complete setup guide (NEW)
├── API_REFERENCE.md                  # API endpoint documentation (NEW)
├── ARCHITECTURE.md                   # System architecture & design (NEW)
├── ENHANCEMENTS.md                   # Project improvements summary (NEW)
├── CLAUDE.md                         # This file
│
├── .env.example                      # Environment template
├── .gitignore
└── SYSTEM_PROMPTS.md                # Agent system prompts specification
```

---

## Key Architectural Patterns

### 1. LangGraph Workflow Pipeline

**Location**: `evaluator/services/langgraph_workflow.py`

9-node sequential pipeline with one parallel stage:

```
Preprocessor → Analyzer → [Evaluator ⟷ DatasetGenerator] → Validator
→ Improver → Revalidator → Comparison → END
```

**Key Points**:
- TypedDict `WorkflowState` passes data between nodes
- Evaluator + DatasetGenerator run in parallel (ThreadPoolExecutor)
- Each node is pure function with clear inputs/outputs
- Fallback to direct execution if graph engine fails
- All state immutable; each node returns new state dict

**When to modify**:
- Adding new evaluation dimensions: update `EVALUATION_DIMENSIONS` in evaluator.py
- Adding new workflow stages: add node + edge in workflow graph
- Changing node execution order: modify `add_edge()` calls

### 2. Service Layer with LLM + Fallback

**Pattern**: Each service has two paths:
1. **LLM Path**: Calls OpenAI/Azure with structured prompts, returns JSON
2. **Fallback Path**: Deterministic generation with heuristics

**Example** (`evaluator.py`):
```python
if llm_client.is_configured():
    res = llm_client.generate_json(SYSTEM_PROMPT, user_content, ...)
    if res and valid_structure(res):
        return res
# Fallback to heuristic scoring
return cls._fallback_evaluate(...)
```

**Benefits**:
- Offline operation without API keys
- Reproducible results in fallback mode
- Graceful degradation on API failures

**When to extend**:
- Adding new service: create class with `generate()` + `_fallback_*()` methods
- Changing LLM logic: update system prompt + JSON schema

### 3. Pydantic Validation at Boundaries

**Location**: `evaluator/schemas.py`

All external inputs validated with Pydantic before reaching business logic.

```python
# In view
try:
    req = EvaluateRequestSchema(**request.data)
except PydanticValidationError as e:
    return Response(format_errors(e), status=400)

# Business logic receives validated data
workflow_result = execute_evaluation_workflow(
    department=req.department,  # Type-safe
    task_type=req.task_type,    # Bounds-checked
    ...
)
```

**Key schemas**:
- `EvaluateRequestSchema`: Request validation (dataset_size: 1-100, prompt: 5-10k chars)
- `EvaluationSchema`: 15-dimension evaluation with score validation
- `SyntheticDatasetSchema`: Test cases with field constraints
- `ComparisonSchema`: Before/after metrics

**When to modify**:
- Adding new API fields: add to schema first, test validation, update view
- Changing bounds: modify Field(..., ge=X, le=Y) constraints
- New dimensions: add to schema, update evaluator

### 4. Custom Exception Hierarchy

**Location**: `evaluator/exceptions.py`

Base `PromptEvaluationException` with specific subclasses:
- `ValidationException` (user error, HTTP 400)
- `LLMException` (system error, HTTP 500)
- `DatasetGenerationException`
- `AnalysisException`
- `EvaluationException`

```python
# In service
if not valid_input:
    raise ValidationException("Input too short", details={...}, is_user_error=True)

# In view
except ValidationException as e:
    return Response(format_error_response(e), status=400)
except LLMException as e:
    logger.error(f"LLM failed: {e.message}")
    return Response(format_error_response(e), status=500)
```

**When to use**:
- Validation failures in views/services: raise specific exception
- Logging: use `logger.log(log_level, msg, exc_info=True)`
- Don't catch exceptions silently; always log or raise

### 5. Middleware for Cross-Cutting Concerns

**Location**: `evaluator/middleware.py`

Two middleware classes in Django MIDDLEWARE stack:

1. **RateLimitMiddleware**: Per-IP rate limiting (60 req/min)
2. **RequestLoggingMiddleware**: Logs all API requests with timing

```python
MIDDLEWARE = [
    ...,
    "evaluator.middleware.RequestLoggingMiddleware",
    "evaluator.middleware.RateLimitMiddleware",
]
```

**When to add**:
- Cross-request concerns (auth, rate limiting, logging)
- Not for business logic (use views/services instead)

---

## Coding Standards & Conventions

### Python (Backend)

**Style Guide**: PEP 8 via Black formatter

```bash
# Format code
black evaluator/

# Check style
flake8 evaluator/

# Sort imports
isort evaluator/
```

**Type Hints**:
```python
# ✅ Always use type hints
def generate(
    cls,
    department: str,
    prompt: str,
    analysis: Dict[str, Any]
) -> Dict[str, Any]:
    ...

# ✅ Use TypedDict for complex dicts
class WorkflowState(TypedDict, total=False):
    department: str
    analysis: Dict[str, Any]
    ...
```

**Error Handling**:
```python
# ✅ Use specific exceptions
raise ValidationException("Invalid prompt", details={...})

# ✅ Log with context
logger.error(f"Failed to evaluate: {e}", exc_info=True)

# ❌ Don't silently catch
try:
    result = llm_client.generate_json(...)
except:  # ❌ TOO BROAD
    pass

# ✅ Be specific
try:
    result = llm_client.generate_json(...)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return None
```

**Logging**:
```python
# ✅ Use appropriate levels
logger.debug("Evaluating prompt")           # Development details
logger.info("Evaluation completed")         # Important state changes
logger.warning("Fallback mode activated")   # Degraded operation
logger.error("LLM API failed", exc_info=True)  # Errors with stack trace

# ❌ Don't use print()
print("Debug info")  # ❌ Won't be logged to file
```

**Comments**:
```python
# ✅ Only document WHY, not WHAT
# Exponential backoff prevents overwhelming transient failures
for attempt in range(max_retries):
    ...

# ❌ Don't state the obvious
x = x + 1  # Increment x
```

### React (Frontend)

**Style**: ES6+, functional components with hooks

```javascript
// ✅ Use hooks for state
const [isLoading, setIsLoading] = useState(false);
const [result, setResult] = useState(null);

// ✅ Use descriptive names
const handleEvaluate = async () => { ... }
const renderDimensionTable = () => { ... }

// ✅ Handle errors
try {
    const res = await fetch('/api/evaluate/', { ... });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    setResult(data);
} catch (err) {
    setError(err.message);
}

// ❌ Don't use dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: html }} />  // ❌ XSS risk

// ✅ Use React content
<div>{sanitizedContent}</div>
```

**CSS**:
```css
/* ✅ Use CSS variables for theming */
:root {
    --text-main: #1a1a1a;
    --bg-primary: #ffffff;
}

[data-theme="dark"] {
    --text-main: #ffffff;
    --bg-primary: #1a1a1a;
}

body {
    color: var(--text-main);
    background: var(--bg-primary);
}
```

---

## Testing Requirements

### Unit Tests

**Location**: `evaluator/tests.py`

**Required coverage**:
- Each service's main method (Analyzer, Evaluator, DatasetGenerator, etc.)
- Fallback modes (test when LLM is unconfigured)
- Edge cases (empty inputs, boundary values)

**Example**:
```python
from django.test import TestCase
from unittest.mock import patch
from evaluator.services.evaluator import Evaluator

class EvaluatorTestCase(TestCase):
    def test_evaluate_with_valid_prompt(self):
        result = Evaluator.evaluate(
            department="software",
            task_type="create docs",
            prompt="Create JWT documentation",
            analysis={}
        )

        self.assertIn("dimensions", result)
        self.assertIn("overall_score", result)
        self.assertEqual(len(result["dimensions"]), 15)

    @patch('evaluator.services.llm_client.llm_client.is_configured', return_value=False)
    def test_fallback_evaluation(self, mock_llm):
        result = Evaluator.evaluate(...)
        self.assertIsNotNone(result)  # Fallback returns result
```

**Run tests**:
```bash
python manage.py test evaluator
python manage.py test evaluator.tests.EvaluatorTestCase
python manage.py test evaluator -v 2  # Verbose output
```

**Coverage**:
```bash
coverage run --source='evaluator' manage.py test evaluator
coverage report
coverage html  # Generate HTML report
```

### Integration Tests

Test full workflow end-to-end:

```python
def test_complete_evaluation_workflow(self):
    response = self.client.post('/api/evaluate/', {
        'department': 'software',
        'task_type': 'create docs',
        'prompt': 'Create comprehensive JWT authentication guide',
        'dataset_size': 5
    })

    self.assertEqual(response.status_code, 200)
    data = response.json()

    # Verify all components present
    self.assertIn('analysis', data)
    self.assertIn('evaluation', data)
    self.assertIn('synthetic_dataset', data)
    self.assertIn('improved_prompt', data)

    # Verify metrics
    self.assertGreater(data['overall_original_score'], 0)
    self.assertGreater(data['overall_improved_score'], data['overall_original_score'])
```

### Edge Cases to Test

```python
# Empty/minimal inputs
test_prompt("", 0, "")  # Should fail validation

# Boundary values
test_prompt("a"*10000, 100, "x")  # Max lengths
test_prompt("brief", 1, "x")      # Min dataset_size

# LLM failures
mock_llm_failure()
test_fallback_activation()  # Should use deterministic generation

# Concurrent requests
load_test(num_concurrent=100)  # Should handle rate limiting
```

---

## Deployment Procedures

### Development

```bash
# 1. Install dependencies
python -m venv venv
source venv/bin/activate  # Or: venv\Scripts\activate
pip install -r requirements.txt

# 2. Environment setup
cp .env.example .env
# Edit .env with your settings

# 3. Database
python manage.py migrate

# 4. Run backend
python manage.py runserver 8000

# 5. Run frontend (in another terminal)
cd frontend
npm install
npm run dev  # Opens http://localhost:5173/
```

### Production

```bash
# 1. Use Gunicorn + Nginx
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.wsgi:application

# 2. Build frontend
cd frontend
npm run build
# Serve dist/ with nginx or CDN

# 3. Use PostgreSQL (not SQLite)
# Set POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT in .env
# psycopg[binary] is in requirements.txt; settings.py switches DB when POSTGRES_HOST is set

# 4. Use Redis for caching
pip install redis django-redis
# Update CACHES in settings.py

# 5. Environment: set DJANGO_DEBUG=False
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY=<secure-key>
```

**Deployment Checklist**:
- [ ] Change SECRET_KEY to random value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS (not "*")
- [ ] Use HTTPS only
- [ ] Set CORS_ALLOW_ALL_ORIGINS to specific domains
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure Redis for caching
- [ ] Set up log aggregation
- [ ] Configure monitoring/alerting
- [ ] Load test before deploying
- [ ] Set up automated backups
- [ ] Enable CSRF protection

---

## Important Gotchas & Constraints

### 1. Dataset Validation is Strict

**Issue**: LLM may return unbalanced difficulty distribution
**Solution**: DatasetValidator rebalances if needed, falls back to deterministic if too skewed
**Don't**: Assume LLM always returns target distribution
**Do**: Check `validation_report_json` for issues detected and repaired

### 2. LLM Client is Resilient but Logs Silently on Fallback

**Issue**: Silent fallback can mask API configuration bugs
**Solution**: Check logs to see if fallback activated
**Don't**: Assume empty LLM response means success
**Do**: Check `logger.warning("No active LLM API keys...")` in logs

### 3. JSONField Data is Write-Once

**Issue**: Can't efficiently query individual dimensions by score
**Solution**: Future: normalize to relational table
**Don't**: Try to filter evaluations by dimension score (won't work efficiently)
**Do**: Load evaluation, parse JSON in Python/JavaScript

### 4. Fallback Mode is Deterministic but Generic

**Issue**: Fallback test cases are template-based, not fully customized
**Solution**: Use LLM mode for production; fallback for testing/offline
**Don't**: Rely on fallback for real evaluations
**Do**: Test both LLM and fallback modes

### 5. ThreadPoolExecutor for Parallel Execution

**Issue**: Uses ThreadPoolExecutor for Evaluator + DatasetGenerator
**Solution**: Good enough for I/O-bound LLM calls; upgrade to async/await if needed
**Don't**: Add CPU-intensive operations to threads
**Do**: Keep to I/O-bound operations (API calls, file I/O)

### 6. Rate Limiting is Per-IP, Not Per-User

**Issue**: Behind proxy, all users appear as same IP
**Solution**: Deploy behind proper reverse proxy that sets X-Forwarded-For
**Don't**: Increase limit arbitrarily
**Do**: Configure proxy to pass real IP in headers

### 7. Excel Export Loads Full Evaluation into Memory

**Issue**: Can't stream large datasets (not memory-efficient)
**Solution**: Fine for typical use (<1000 test cases); optimize if needed
**Don't**: Export datasets > 10,000 cases at once
**Do**: Implement pagination for Excel export if needed

---

## Tools & Commands

### Essential Commands

```bash
# Backend
python manage.py runserver              # Start dev server
python manage.py migrate                # Apply DB migrations
python manage.py makemigrations         # Create migration files
python manage.py test evaluator         # Run tests
python manage.py test evaluator -v 2    # Verbose tests
python manage.py shell                  # Interactive Python shell

# Code Quality
black evaluator/                        # Format code
flake8 evaluator/                       # Lint
isort evaluator/                        # Sort imports

# Frontend
npm run dev                              # Dev server (http://localhost:5173/)
npm run build                            # Production build
npm run preview                          # Preview production build

# Database
sqlite3 db.sqlite3 ".schema"             # View schema
sqlite3 db.sqlite3 "SELECT * FROM evaluator_promptevaluation LIMIT 5;"

# Logging
tail -f logs/django.log                  # Watch logs
tail -f logs/evaluator_services_llm_client.log
```

### Debugging

```python
# Django shell
python manage.py shell
>>> from evaluator.models import PromptEvaluation
>>> eval = PromptEvaluation.objects.first()
>>> eval.evaluation_json['overall_score']
6.5

# Breakpoint
import pdb; pdb.set_trace()

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Development Workflow

### Adding a New Feature

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-evaluation-dimension
   ```

2. **Add schema validation** (if API change):
   ```python
   # evaluator/schemas.py
   class NewSchema(BaseModel):
       field: str = Field(..., max_length=100)
   ```

3. **Implement feature**:
   ```python
   # evaluator/services/new_service.py
   class NewService:
       def execute(self, ...):
           # Implementation
           pass

       def _fallback_execute(self, ...):
           # Fallback logic
           pass
   ```

4. **Add tests**:
   ```python
   # evaluator/tests.py
   class NewServiceTestCase(TestCase):
       def test_feature(self):
           result = NewService.execute(...)
           self.assertIsNotNone(result)
   ```

5. **Update docs**:
   - Update ARCHITECTURE.md if adding new service
   - Update API_REFERENCE.md if changing API
   - Add comments in code for non-obvious logic

6. **Run tests & lint**:
   ```bash
   python manage.py test evaluator
   black evaluator/
   flake8 evaluator/
   ```

7. **Commit with clear message**:
   ```bash
   git commit -m "Add new evaluation dimension: X

   - Added dimension to evaluator schema
   - Implemented LLM and fallback logic
   - Added test coverage
   - Updated documentation"
   ```

8. **Create pull request** with description

### Common Modifications

**Adding a new evaluation dimension**:
1. Add to `EVALUATION_DIMENSIONS` list in evaluator.py
2. Update system prompt in evaluator.py
3. Add to fallback heuristics
4. Add test case
5. Update SYSTEM_PROMPTS.md

**Changing dataset size calculation**:
1. Modify `_calculate_distribution()` in dataset_generator.py
2. Update validation tolerance in validator.py
3. Test with various sizes (1, 5, 10, 20, 100)

**Adding new API endpoint**:
1. Create view in views.py
2. Add URL in urls.py
3. Add Pydantic schema in schemas.py
4. Add tests
5. Document in API_REFERENCE.md

---

## Key Files Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `backend/settings.py` | Django config | Adding middleware, caching, logging |
| `evaluator/models.py` | Database schema | Changing data structure |
| `evaluator/schemas.py` | Request validation | New API fields |
| `evaluator/views.py` | API endpoints | New endpoints, validation changes |
| `evaluator/services/` | Business logic | Core algorithm changes |
| `SYSTEM_PROMPTS.md` | Agent instructions | Improving evaluation quality |
| `frontend/src/App.jsx` | Frontend logic | UI flow changes |
| `requirements.txt` | Dependencies | Adding packages |

---

## Documentation References

- **Setup & Installation**: See `SETUP.md`
- **API Endpoints**: See `API_REFERENCE.md`
- **System Architecture**: See `ARCHITECTURE.md`
- **Enhancements & Changes**: See `ENHANCEMENTS.md`
- **Agent Prompts**: See `SYSTEM_PROMPTS.md`
- **Original Project**: See `README.md`

---

## Performance Considerations

### Request Latency

Expected timing per evaluation:
- Preprocessing: ~100ms
- Analysis: 1-2 seconds
- Evaluation + Dataset Generation: 2-4 seconds (parallel)
- Validation: ~100ms
- Improvement: 1-2 seconds
- Re-validation: 1-2 seconds
- **Total: 3-8 seconds** (varies by LLM latency)

### Database

- **Current**: SQLite (suitable for development)
- **Production**: Migrate to PostgreSQL with connection pooling
- **Indexes**: Added on prompt_id, created_at, overall_original_score
- **JSONField**: Use for evaluation data (write-once); normalize if ad-hoc querying needed

### Caching

- **Current**: In-memory LocMemCache (5-min TTL)
- **Production**: Use Redis for distributed caching
- **What to cache**: Evaluation results, static resources
- **What NOT to cache**: LLM responses (for freshness)

### Concurrency

- **Rate limit**: 60 requests/minute per IP
- **Max workers**: ThreadPoolExecutor(max_workers=2) for Evaluator + DatasetGenerator
- **Database**: SQLite is single-threaded; PostgreSQL supports 100+ concurrent connections

---

## Security Notes

### Input Validation
- ✅ All requests validated with Pydantic
- ✅ Bounds checking on all fields
- ✅ No SQL injection (ORM only)
- ✅ No XSS (React escaping)

### Data Protection
- ⚠️ API keys in .env (never commit to git)
- ⚠️ Logs may contain prompt text (PII)
- ⚠️ No authentication/authorization yet (add if needed)

### API Security
- ✅ CORS configurable (restrict in production)
- ✅ Rate limiting enabled
- ✅ Error messages sanitized
- ⚠️ Set DEBUG=False in production

---

## Troubleshooting

### LLM API Not Configured
- **Check**: `.env` file exists and has valid API key
- **Check**: `logger.info("No active LLM API keys...")` in logs
- **Solution**: System automatically uses fallback mode

### Rate Limit Exceeded
- **Check**: `HTTP 429 Too Many Requests` response
- **Solution**: Wait 60 seconds, implement request queueing

### Tests Failing
- **Check**: `python manage.py test evaluator -v 2`
- **Check**: Migrations applied: `python manage.py migrate`
- **Solution**: Mock LLM in tests with `@patch('evaluator.services.llm_client...')`

### Frontend Can't Reach Backend
- **Check**: Backend running on port 8000
- **Check**: CORS enabled (should be by default)
- **Solution**: Update `VITE_API_BASE_URL` in frontend if needed

### Logs Not Appearing
- **Check**: Logs directory exists: `mkdir logs`
- **Check**: Permissions on logs directory
- **Solution**: Check `backend/settings.py` logging configuration

---

## Contributors

For commits, use format:
```
[TYPE] Brief description

Detailed explanation

Fixes #123 (if applicable)
```

Types: `[FEATURE]`, `[FIX]`, `[REFACTOR]`, `[DOCS]`, `[TEST]`, `[PERF]`

Example:
```
[FEATURE] Add difficulty distribution validation to dataset generator

- Validates LLM-generated test cases against target distribution
- Falls back to deterministic generation if distribution is skewed
- Logs all validation results for debugging

Fixes #45
```

---

## Last Updated

- **Created**: 2026-10-01
- **Last Modified**: 2026-10-01
- **Maintained By**: Development Team
- **Current Version**: 1.0 (Production-ready)

For questions, refer to documentation files or check logs for debugging information.
