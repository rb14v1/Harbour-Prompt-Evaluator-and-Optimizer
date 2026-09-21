# Project Structure

## Directory Tree

```
prompt-evaluator-and-optimizer/
├── README.md                          # User-facing project guide
├── CLAUDE.md                          # Technical architecture documentation
├── SYSTEM_PROMPT.md                   # LLM system prompt
├── SETUP.md                           # Development setup guide
├── DEVELOPMENT.md                     # Development progress tracker
├── PROJECT_STRUCTURE.md               # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
│
├── backend/                           # Django backend
│   ├── manage.py                      # Django management script
│   │
│   ├── config/                        # Django project configuration
│   │   ├── __init__.py
│   │   ├── settings.py                # Django settings
│   │   ├── urls.py                    # URL routing
│   │   └── wsgi.py                    # WSGI application
│   │
│   ├── evaluator/                     # Main Django app
│   │   ├── __init__.py
│   │   ├── apps.py                    # App configuration
│   │   ├── admin.py                   # Django admin registration
│   │   ├── models.py                  # Database models (7 models)
│   │   ├── serializers.py             # DRF serializers (8 classes)
│   │   ├── views.py                   # API views (2 ViewSets)
│   │   ├── orchestrator.py            # Main pipeline orchestrator
│   │   ├── tests.py                   # Unit and integration tests
│   │   │
│   │   ├── agents/                    # Core agent modules
│   │   │   ├── __init__.py
│   │   │   ├── preprocessor.py        # Text normalization agent
│   │   │   ├── classifier.py          # Task classification agent (Azure OpenAI)
│   │   │   ├── analyzer.py            # Prompt decomposition agent (Azure OpenAI)
│   │   │   ├── validator.py           # 8-dimension validation agent (Azure OpenAI)
│   │   │   ├── scoring_engine.py      # Numerical scoring agent
│   │   │   ├── improver.py            # Prompt rewriting agent (Azure OpenAI)
│   │   │   └── report.py              # Report generation agent
│   │   │
│   │   └── migrations/                # Database migrations (auto-generated)
│   │       └── __init__.py
│   │
│   └── data/                          # Datasets
│       ├── classification_dataset.json # Task classification examples (10 samples)
│       └── validation_reference.json   # Validation dimension examples (32 samples)
│
├── frontend/                          # React + Vite (NOT YET CREATED)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── .gitignore                         # Git ignore rules
```

## File Descriptions

### Documentation
| File | Purpose | Lines |
|------|---------|-------|
| README.md | User-facing guide with examples | 550+ |
| CLAUDE.md | Technical architecture & implementation guide | 850+ |
| SYSTEM_PROMPT.md | Complete LLM system prompt | 650+ |
| SETUP.md | Development setup instructions | 400+ |
| DEVELOPMENT.md | Progress tracking & task list | 400+ |
| PROJECT_STRUCTURE.md | This file | 300+ |

### Configuration
| File | Purpose |
|------|---------|
| requirements.txt | Python dependencies (13 packages) |
| .env.example | Environment variables template |
| backend/config/settings.py | Django settings |
| backend/config/urls.py | API URL routing |
| backend/config/wsgi.py | WSGI application entry point |

### Database & Models
| File | Classes | Purpose |
|------|---------|---------|
| evaluator/models.py | 7 models | Core database schema |
| | Prompt | User prompts storage |
| | Classification | Task type & complexity |
| | Analysis | Prompt decomposition |
| | DimensionScore | Individual dimension ratings |
| | Evaluation | Comprehensive evaluation |
| | PromptImprovement | Iterative improvements |
| | EvaluationResult | Final results |

### Agents
| File | Class | Purpose | Uses Azure OpenAI |
|------|-------|---------|-------------------|
| preprocessor.py | PreprocessorAgent | Text normalization | No |
| classifier.py | ClassifierAgent | Task classification | Yes (4-5 calls) |
| analyzer.py | AnalyzerAgent | Prompt decomposition | Yes (1 call) |
| validator.py | ValidatorAgent | 8-dimension evaluation | Yes (1 call) |
| scoring_engine.py | ScoringEngine | Numerical scoring | No |
| improver.py | ImproverAgent | Prompt rewriting | Yes (up to 3 calls) |
| report.py | ReportAgent | Report generation | No |

### API & Views
| File | Classes | Purpose |
|------|---------|---------|
| orchestrator.py | PromptEvaluationOrchestrator | Main pipeline controller |
| serializers.py | 8 serializer classes | Request/response validation |
| views.py | 2 ViewSet classes | REST API endpoints |
| admin.py | 7 ModelAdmin classes | Django admin interface |

### Testing
| File | Purpose |
|------|---------|
| evaluator/tests.py | Unit & integration tests (200+ lines) |

### Datasets
| File | Purpose | Samples |
|------|---------|---------|
| classification_dataset.json | Training examples for classifier | 10 prompts |
| validation_reference.json | Dimension quality examples | 32 examples (8 dims × 4 levels) |

## API Endpoints

### Evaluation Endpoints
```
POST   /api/evaluations/evaluate/              # Evaluate single prompt
POST   /api/evaluations/batch_evaluate/        # Evaluate multiple prompts
GET    /api/evaluations/<id>/detail/           # Get evaluation details
GET    /api/evaluations/                       # List all evaluations
```

### History Endpoints
```
GET    /api/history/                           # List all prompts
GET    /api/history/<id>/evaluations/          # Get prompt's evaluations
GET    /api/history/stats/                     # Get user statistics
```

## Data Models

### Prompt Model
```python
id: UUID
user: ForeignKey(User)
original_prompt: TextField
processed_prompt: TextField
created_at: DateTime
updated_at: DateTime
```

### Classification Model
```python
id: UUID
prompt: OneToOneField(Prompt)
task_type: CharField (9 choices)
complexity: CharField (3 levels)
confidence: FloatField (0.0-1.0)
reasoning: TextField
created_at: DateTime
```

### Analysis Model
```python
id: UUID
prompt: OneToOneField(Prompt)
intent: TextField
requirements: JSONField (list)
context: JSONField (list)
constraints: JSONField (list)
expected_output: TextField
missing_information: JSONField (list)
ambiguities: JSONField (list)
created_at: DateTime
```

### Evaluation Model
```python
id: UUID
prompt: OneToOneField(Prompt)
dimension_scores: ManyToManyField(DimensionScore)
overall_score: FloatField
threshold: FloatField (default 7.0)
status: CharField ('needs_improvement', 'ready')
low_scoring_dimensions: JSONField (list)
high_performing_dimensions: JSONField (list)
created_at: DateTime
updated_at: DateTime
```

### PromptImprovement Model
```python
id: UUID
original_prompt: ForeignKey(Prompt)
improved_prompt: TextField
iteration_number: IntegerField
changes_made: JSONField (list)
dimensions_addressed: JSONField (list)
intent_preserved: BooleanField
reasoning: TextField
created_at: DateTime
```

### EvaluationResult Model
```python
id: UUID
prompt: OneToOneField(Prompt)
original_prompt: TextField
final_prompt: TextField
initial_score: FloatField
final_score: FloatField
improvements_made: IntegerField
iterations_required: IntegerField
summary: TextField
status: CharField ('ready', 'needs_manual_review')
full_report: JSONField
created_at: DateTime
```

## Agent Pipeline Flow

```
Raw Prompt
    ↓
Preprocessor
    ├─ Normalize text
    ├─ Preserve original
    └─ Extract metadata
    ↓
Classifier (Azure OpenAI)
    ├─ Categorize task (9 types)
    ├─ Assess complexity (3 levels)
    └─ Generate confidence (0.0-1.0)
    ↓
Analyzer (Azure OpenAI)
    ├─ Extract intent
    ├─ Identify requirements
    ├─ List context
    ├─ Define constraints
    ├─ Describe expected output
    └─ Note gaps & ambiguities
    ↓
Validator (Azure OpenAI)
    ├─ Evaluate clarity (10.0 scale)
    ├─ Evaluate specificity
    ├─ Evaluate context
    ├─ Evaluate completeness
    ├─ Evaluate requirements
    ├─ Evaluate constraints
    ├─ Evaluate expected_output
    └─ Evaluate actionability
    ↓
Scoring Engine
    ├─ Convert to numerical scores
    ├─ Calculate overall score
    ├─ Compare to threshold (7.0)
    └─ Identify low-scoring dimensions
    ↓
Decision: Score ≥ 7.0?
    ├─ YES → Report Agent
    └─ NO → Improver (if iterations < 3)
    ↓
Improver (Azure OpenAI, up to 3 times)
    ├─ Rewrite prompt
    ├─ Address low-scoring dimensions
    ├─ Preserve intent
    └─ Document changes
    ↓
[Loop back to Validator/Scoring]
    ↓
Report Agent
    ├─ Aggregate all results
    ├─ Compile improvement history
    ├─ Generate summary
    └─ Return final report
    ↓
Final Report
```

## Azure OpenAI Integration

All LLM calls go through Azure OpenAI with these agent responsibilities:

| Agent | LLM Calls | Purpose |
|-------|-----------|---------|
| Classifier | 1 | Categorize task type, assess complexity |
| Analyzer | 1 | Decompose prompt into components |
| Validator | 1 | Evaluate across 8 dimensions |
| Improver | 1-3 | Rewrite prompt (max 3 iterations) |
| **Total** | **4-6** | Per prompt evaluation |

Configuration via environment variables:
- `AZURE_OPENAI_API_KEY` – API authentication
- `AZURE_OPENAI_ENDPOINT` – Service endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME` – Model deployment (default: gpt-4)
- `AZURE_OPENAI_API_VERSION` – API version (default: 2024-02-15-preview)

## Environment Configuration

All settings configurable via `.env`:

**Django**
- `DEBUG` – Debug mode (True/False)
- `DJANGO_SECRET_KEY` – Secret key for cryptography
- `ALLOWED_HOSTS` – Comma-separated list of allowed hosts

**Database**
- `DB_NAME` – PostgreSQL database name
- `DB_USER` – Database user
- `DB_PASSWORD` – Database password
- `DB_HOST` – Database host
- `DB_PORT` – Database port

**Azure OpenAI**
- `AZURE_OPENAI_API_KEY` – API key
- `AZURE_OPENAI_ENDPOINT` – Endpoint URL
- `AZURE_OPENAI_DEPLOYMENT_NAME` – Model name
- `AZURE_OPENAI_API_VERSION` – API version

**Azure Storage**
- `AZURE_STORAGE_CONNECTION_STRING` – Connection string
- `AZURE_STORAGE_CONTAINER_NAME` – Container name

**CORS**
- `CORS_ALLOWED_ORIGINS` – Comma-separated list of allowed origins

**Application**
- `MAX_ITERATIONS` – Max improvement iterations (default: 3)
- `THRESHOLD` – Quality threshold (default: 7.0)

## Dependencies

Core packages (from requirements.txt):
- Django 4.2.9 – Web framework
- djangorestframework 3.14.0 – REST API
- openai 1.3.9 – Azure OpenAI client
- psycopg2-binary 2.9.9 – PostgreSQL adapter
- azure-storage-blob 12.19.0 – Azure Storage
- celery 5.3.4 – Task queue (optional)

## Testing

Test file includes:
- PreprocessorAgent tests
- ScoringEngine tests
- Model tests
- Orchestrator tests
- Integration tests

Run with:
```bash
python manage.py test
```

## What's Implemented ✅

- [x] All 6 core agents
- [x] Database models
- [x] REST API endpoints
- [x] Azure OpenAI integration
- [x] Scoring system
- [x] Improvement loop (max 3 iterations)
- [x] Report generation
- [x] Sample datasets
- [x] Unit tests
- [x] Django admin interface

## What's Not Implemented Yet ❌

- [ ] React + Vite frontend
- [ ] Authentication (uses Django default)
- [ ] Rate limiting
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Caching layer
- [ ] Logging & monitoring
- [ ] Docker setup
- [ ] CI/CD pipeline
- [ ] E2E tests
- [ ] Database optimization

## Next Steps

1. **Verify Setup** – Run migrations, test API with Postman
2. **Test Agents** – Verify Azure OpenAI integration works
3. **Build Frontend** – Create React app with Vite
4. **Add Tests** – Write comprehensive test suite
5. **Deploy** – Set up Docker and CI/CD

---

**Last Updated:** 2026-09-09  
**Total Files Created:** 30+  
**Total Lines of Code:** 5,000+  
**Backend Status:** ✅ Ready for testing  
**Frontend Status:** ⏳ Not started
