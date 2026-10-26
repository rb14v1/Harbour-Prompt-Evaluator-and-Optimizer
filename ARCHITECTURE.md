# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND (React 19)                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  EvaluationForm │ DimensionsTable │ SyntheticDatasetView   │  │
│  │  PromptComparison │ AnalysisView │ SummaryCards │ History  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                    REST API (JSON)
                             │
┌────────────────────────────┼──────────────────────────────────────┐
│                    DJANGO REST API                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Views (Request Validation, Error Handling)             │     │
│  │  EvaluatePromptView, EvaluationListView, ExportView    │     │
│  └──────────────────┬──────────────────────────────────────┘     │
│                     │                                             │
│  ┌──────────────────┼──────────────────────────────────────┐     │
│  │    LangGraph Workflow Pipeline                          │     │
│  │                                                         │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │  1. Preprocessor  →  2. Analyzer               │   │     │
│  │  │  ↓                                              │   │     │
│  │  │  3. Evaluator    ⟷  4. Dataset Generator       │   │     │
│  │  │                      (Parallel)                 │   │     │
│  │  │  ↓                                              │   │     │
│  │  │  5. Dataset Validator  →  6. Scorer            │   │     │
│  │  │  ↓                                              │   │     │
│  │  │  7. Improver  →  8. Revalidator               │   │     │
│  │  │  ↓                                              │   │     │
│  │  │  9. Comparison  →  Report Generation           │   │     │
│  │  └─────────────────────────────────────────────────┘   │     │
│  └──────────────────┬──────────────────────────────────────┘     │
│                     │                                             │
│  ┌──────────────────┼──────────────────────────────────────┐     │
│  │ Services Layer                                          │     │
│  │ ├─ Analyzer (Semantic extraction)                       │     │
│  │ ├─ Evaluator (15-dimension scoring)                     │     │
│  │ ├─ DatasetGenerator (Synthetic test case creation)      │     │
│  │ ├─ DatasetValidator (Quality checking & repair)         │     │
│  │ ├─ Improver (Prompt optimization)                       │     │
│  │ ├─ Revalidator (Re-evaluation of improved prompt)       │     │
│  │ ├─ Scorer (Metrics & comparisons)                       │     │
│  │ ├─ LLMClient (Azure OpenAI / OpenAI with fallback)      │     │
│  │ └─ ExcelExporter (Workbook generation)                  │     │
│  └──────────────────┬──────────────────────────────────────┘     │
│                     │                                             │
└─────────────────────┼─────────────────────────────────────────────┘
                      │
          ┌───────────┴──────────────┐
          │                          │
    ┌─────┴──────┐          ┌────────┴─────┐
    │ SQLite DB  │          │   LLM API    │
    │ (Django    │          │ (Azure or    │
    │  ORM)      │          │  OpenAI)     │
    └────────────┘          └──────────────┘
```

## Component Architecture

### Frontend (`frontend/`)

**Framework**: React 19 with Vite

**Key Components**:
- `App.jsx`: Main application shell, state management, routing
- `Header.jsx`: Navigation, theme toggle, export button
- `EvaluationForm.jsx`: Input form for department, task_type, prompt
- `DimensionsTable.jsx`: 15-dimension score visualization
- `SyntheticDatasetView.jsx`: Test cases table with filtering
- `PromptComparison.jsx`: Before/after prompt comparison
- `PromptAnalysisView.jsx`: Semantic analysis details
- `SummaryCards.jsx`: KPI cards (original score, improved score, difference)
- `HistoryModal.jsx`: Evaluation history with pagination

**Styling**: Vanilla CSS with CSS variables for theming (dark/light mode)

**State Management**: React hooks (useState, useEffect) with localStorage for theme persistence

---

### Backend (`backend/` + `evaluator/`)

#### Models (`evaluator/models.py`)

```python
PromptEvaluation
├── prompt_id (CharField, unique)
├── department (CharField)
├── task_type (CharField)
├── original_prompt (TextField)
├── processed_prompt (TextField)
├── analysis_json (JSONField)
├── evaluation_json (JSONField)
├── improved_prompt (TextField)
├── improvement_metadata_json (JSONField)
├── re_evaluation_json (JSONField)
├── comparison_json (JSONField)
├── overall_original_score (FloatField)
├── overall_improved_score (FloatField)
├── score_difference (FloatField)
└── created_at (DateTimeField)

SyntheticDataset (OneToOne → PromptEvaluation)
├── dataset_size (IntegerField)
├── summary_json (JSONField)
├── validation_report_json (JSONField)
└── test_cases (Reverse FK)

SyntheticTestCase (ForeignKey → SyntheticDataset)
├── test_case_id (CharField)
├── input_text (TextField)
├── expected_output (TextField)
├── difficulty (CharField: Easy/Medium/Hard)
├── category (CharField)
├── edge_case (BooleanField)
├── notes (TextField)
└── created_at (DateTimeField)
```

#### Views (`evaluator/views.py`)

**EvaluatePromptView (POST /api/evaluate/)**
- Validates request with Pydantic
- Calls LangGraph workflow
- Persists results to database
- Returns complete evaluation

**EvaluationListView (GET /api/evaluations/)**
- Pagination support (page, page_size)
- Filtering (search by prompt_id, department, task_type)
- Ordering (by created_at, score, score_difference)

**EvaluationDetailView (GET /api/evaluations/<id>/)**
- Retrieves full evaluation with nested dataset

**ExportExcelView (GET /api/evaluations/<id>/export-excel/)**
- Fetches evaluation from database
- Generates Excel workbook
- Returns as downloadable file

**DirectExportExcelView (POST /api/export-excel/)**
- Accepts evaluation JSON payload
- Generates Excel directly (no DB persistence)

#### Services Layer

**LLMClient** (`services/llm_client.py`)
- Unified interface for Azure OpenAI + OpenAI
- Retry logic with exponential backoff
- Graceful fallback to deterministic mode if no API configured
- JSON parsing with validation
- Error logging and metrics

**Analyzer** (`services/analyzer.py`)
- System prompt: Expert Prompt Analyzer
- Extracts: intent, objectives, requirements, constraints, failure modes, risks, edge cases
- Fallback: Heuristic analysis based on keywords and structure
- Output: AnalysisSchema

**Evaluator** (`services/evaluator.py`)
- System prompt: Principal Prompt Engineering Auditor
- Scores 15 dimensions on 0-10 scale
- Calculates overall score (average of 15 dimensions)
- Fallback: Heuristic scoring based on word count, structure, keywords
- Output: EvaluationSchema

**DatasetGenerator** (`services/dataset_generator.py`)
- System prompt: Synthetic Dataset Generation Agent
- Generates Easy (30%), Medium (45%), Hard (25%) test cases
- Dynamic categories based on dept/task/prompt keywords
- NEW: Validates difficulty distribution from LLM output
- Fallback: Deterministic generation with templated variations
- Output: SyntheticDatasetSchema

**DatasetValidator** (`services/dataset_validator.py`)
- Schema validation (required fields, min/max lengths)
- Difficulty distribution balancing
- Deduplication with fuzzy matching (75% similarity threshold)
- Category normalization
- Edge case consistency
- Output: Validated dataset + validation report

**Improver** (`services/improver.py`)
- System prompt: World-Class AI Prompt Optimization Engineer
- Restructures prompt into modular sections
- Addresses identified evaluation weaknesses
- Preserves user intent strictly
- Fallback: Deterministic structuring with standard sections
- Output: Improved prompt + metadata

**Revalidator** (`services/revalidator.py`)
- System prompt: Independent LLM Benchmark Auditor
- Re-evaluates improved prompt using same 15 dimensions
- Independent scoring (no awareness of original scores)
- Output: Re-evaluation results

**Scorer** (`services/scorer.py`)
- Calculates dataset summary (categories, difficulty distribution, edge case count)
- Compares original vs. improved evaluations
- Identifies improvement dimensions, unchanged, and regressions
- Generates key insights

**ExcelExporter** (`services/excel_exporter.py`)
- Creates multi-tab Excel workbook using openpyxl
- Tabs: Executive Summary, Synthetic Dataset, 15-Dimension Scores, Comparison, Semantic Analysis
- Formatting: Headers, alternating row colors, frozen panes
- Output: BytesIO stream ready for download

#### Validation & Error Handling

**Pydantic Schemas** (`evaluator/schemas.py`)
- Request validation: EvaluateRequestSchema
- Response validation: PromptEvaluationResponseSchema, EvaluationSchema, etc.
- Bounds checking: dataset_size (1-100), prompt (5-10000 chars), etc.
- Type safety across entire pipeline

**Exceptions** (`evaluator/exceptions.py`)
- PromptEvaluationException (base)
- ValidationException, LLMException, DatasetGenerationException, etc.
- Contextual error codes and details
- User-vs-system error categorization

#### Middleware & Utilities

**Middleware** (`evaluator/middleware.py`)
- RateLimitMiddleware: 60 requests/minute per IP
- RequestLoggingMiddleware: Logs all API requests/responses with timing

**Logging** (`evaluator/logging_config.py`)
- Console + rotating file handlers
- Structured logging with timestamps
- Log levels: DEBUG (file), INFO (console)

---

## Workflow Pipeline (LangGraph)

```
┌─────────────────────────────────────────────────────────────────┐
│ WorkflowState (TypedDict)                                        │
│ ├─ Inputs: department, task_type, original_prompt, dataset_size │
│ ├─ Outputs: analysis, evaluation, synthetic_dataset, etc.       │
│ └─ Metrics: overall_original_score, score_difference            │
└────────────────┬────────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │ Preprocessor Node       │
    │ (Normalize & clean)     │
    └────────────┬────────────┘
                 │
    ┌────────────┴────────────┐
    │ Analyzer Node           │
    │ (Extract semantics)     │
    └────────────┬────────────┘
                 │
    ┌────────────┴─────────────────────────────┐
    │ Parallel: Evaluator & Dataset Generator  │
    │ ├─ ThreadPoolExecutor (2 workers)        │
    │ ├─ Evaluator: Score 15 dimensions        │
    │ └─ DatasetGenerator: Create test cases   │
    └────────────┬─────────────────────────────┘
                 │
    ┌────────────┴──────────────┐
    │ Dataset Validator Node    │
    │ (Check & repair)          │
    └────────────┬──────────────┘
                 │
    ┌────────────┴──────────────┐
    │ Improver Node             │
    │ (Optimize prompt)         │
    └────────────┬──────────────┘
                 │
    ┌────────────┴──────────────┐
    │ Revalidator Node          │
    │ (Re-evaluate improved)    │
    └────────────┬──────────────┘
                 │
    ┌────────────┴──────────────┐
    │ Comparison Node           │
    │ (Calculate deltas)        │
    └────────────┬──────────────┘
                 │
              [END]
```

---

## Data Flow

```
User Input (department, task_type, prompt)
        ↓
EvaluatePromptView (Request Validation with Pydantic)
        ↓
execute_evaluation_workflow()
        ↓
[LangGraph Pipeline executes all 9 nodes]
        ↓
workflow_result (complete evaluation data)
        ↓
Persist to Database (ORM)
        ├─ PromptEvaluation
        ├─ SyntheticDataset
        └─ SyntheticTestCase[]
        ↓
Response JSON returned to client
        ↓
Frontend renders all 4 tabs: Dataset | Dimensions | Comparison | Analysis
```

---

## Fallback Mode Architecture

```
If LLM API configured:
    Use Azure OpenAI / OpenAI with retry logic
Else:
    Use intelligent deterministic generation
    ├─ Analyzer: Heuristic analysis
    ├─ Evaluator: Heuristic scoring
    ├─ DatasetGenerator: Templated variations
    ├─ Improver: Deterministic structuring
    └─ Revalidator: Deterministic re-scoring
```

Benefits:
- Offline operation without API keys
- Reproducible results
- No external dependencies
- Predictable performance

---

## Database Schema

**Indexes**:
- PromptEvaluation.prompt_id (unique)
- PromptEvaluation.created_at
- PromptEvaluation.overall_original_score

**Foreign Key Constraints**:
- SyntheticDataset.evaluation_id → PromptEvaluation.id (CASCADE)
- SyntheticTestCase.dataset_id → SyntheticDataset.id (CASCADE)

**JSONField Rationale** (vs. relational normalization):
- Evaluation data is write-once, rarely queried
- Storing as JSON simplifies persistence
- Future optimization: normalize dimensions to relational table for ad-hoc querying

---

## Performance Characteristics

| Operation | Time | Parallelization |
|-----------|------|-----------------|
| Preprocessing | ~0.1s | Sequential |
| Analysis | 1-2s | Sequential |
| Evaluation + Dataset Gen | 2-4s | Parallel (ThreadPoolExecutor) |
| Validation | ~0.1s | Sequential |
| Improvement | 1-2s | Sequential |
| Re-validation | 1-2s | Sequential |
| Comparison | ~0.05s | Sequential |
| **Total** | **3-8s** | **Optimal** |

---

## Caching Strategy

- **Evaluation results**: 5 minutes (LocMemCache)
- **Dataset deduplication**: In-memory during validation
- **LLM responses**: Not cached (by design, for freshness)

Future: Redis for distributed caching

---

## Security Layers

1. **Input Validation**: Pydantic schemas with bounds
2. **Rate Limiting**: 60 req/min per IP
3. **CORS**: Whitelist-able in production
4. **No SQL Injection**: ORM-only queries
5. **No XSS**: React escaping + no dangerouslySetInnerHTML
6. **Environment Secrets**: API keys in .env, not in code
7. **Logging**: Sensitive data excluded from logs

---

## Deployment Options

**Development**: Django dev server + Vite dev server

**Production**:
```
WSGI: gunicorn or waitress
Frontend: static build served by nginx/apache
DB: PostgreSQL with connection pooling
Cache: Redis (optional, for distributed caching)
```

---

## Monitoring & Observability

**Logs**:
- `logs/django.log`: Django framework events
- `logs/evaluator_*.log`: Service-specific debug info

**Metrics** (to be added):
- Request latency histograms
- LLM token consumption
- Cache hit rates
- Error rates by type

---

## Extensibility Points

1. **New Evaluation Dimensions**: Add to `EVALUATION_DIMENSIONS` in evaluator.py
2. **New Dataset Categories**: Extend `_derive_dynamic_categories()` in dataset_generator.py
3. **New LLM Provider**: Extend `LLMClient` with provider initialization
4. **New Export Formats**: Add exporter classes to `services/`
5. **Custom Fallback Logic**: Override `_fallback_*` methods in any service

---

## Testing Strategy

- Unit tests for each service (mock LLM)
- Integration tests for full workflow
- Edge case tests for fallback modes
- Load tests for concurrent requests

See `evaluator/tests.py` for examples.
