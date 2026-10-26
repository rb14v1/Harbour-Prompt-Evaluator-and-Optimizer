# Prompt Evaluation & Optimization System with Prompt-Specific Synthetic Dataset Generation

A full-stack, enterprise-grade AI system that evaluates user prompts across **15 standardized quality dimensions**, generates **prompt-specific synthetic test datasets**, automatically optimizes prompts, re-evaluates improvements, and exports reports into a multi-tab formatted Excel workbook.

---

## Architecture & Workflow

```text
                                FRONTEND
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                Department                    Task Type
                     │                           │
                     └─────────────┬─────────────┘
                                   │
                                 Prompt
                                   │
                                   ▼
                            PREPROCESSOR
                                   │
                                   ▼
                                ANALYZER
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
             PROMPT EVALUATOR             SYNTHETIC DATASET
               15 DIMENSIONS                 GENERATOR
                    │                             │
                    │                             ▼
                    │                       DATASET VALIDATOR
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
                                SCORER
                                   │
                                   ▼
                               IMPROVER
                                   │
                                   ▼
                             RE-VALIDATOR
                                   │
                                   ▼
                        BEFORE/AFTER COMPARISON
                                   │
                                   ▼
                            REPORT GENERATOR
                                   │
                                   ▼
                              EXCEL REPORT
```

### Core Architecture Highlights

1. **Frontend Metadata is Authoritative**: `department`, `task_type`, and `prompt` are passed directly from the frontend. **No Classifier Agent is used.**
2. **15 Evaluation Dimensions (0–10 Scale)**:
   - Instruction Following, Clarity, Specificity, Context Completeness, Output Format, Constraints, Robustness, Ambiguity (10=unambiguous), Safety, Reusability, Maintainability, LLM Friendliness, Token Efficiency, Scalability, Overall Prompt Design.
3. **Prompt-Specific Synthetic Dataset Generator**:
   - Generates realistic test cases specifically for the prompt's domain, intent, and schema.
   - Configurable size (default `20`).
   - Meaningful difficulty distribution (Easy ~30%, Medium ~45%, Hard ~25%).
   - Dynamic domain categories (e.g. Authentication Flow, API Specification, Edge Case Inputs, Nested Schemas).
   - Validates schema, deduplicates, checks edge case coverage, and repairs invalid entries deterministically.
4. **Improver & Re-Validator**:
   - Re-engineers prompts into modular structures with explicit constraints and schema guardrails while strictly preserving user intent.
   - Independently re-evaluates the improved prompt across all 15 dimensions.
5. **Excel Export (`openpyxl`)**:
   - Generates a multi-tab workbook with Executive Summary, Synthetic Dataset Table, 15-Dimension Scoring, Prompt Comparison, and Semantic Analysis.

---

## Technology Stack

- **Backend**: Python 3, Django 4.2, Django REST Framework, LangGraph, SQLite, OpenPyXL, Azure OpenAI / OpenAI
- **Frontend**: React 19, Vite, Vanilla CSS, Lucide React

---

## Configuration & Environment Variables

Create a `.env` file in the root directory (or copy from `.env.example`):

```bash
cp .env.example .env
```

Configure your Azure OpenAI credentials in `.env`:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True

# Azure OpenAI Credentials
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

> **Security Note**: Never hardcode credentials. When no API key is provided, the system automatically runs with an intelligent deterministic fallback engine, enabling seamless offline testing.

---

## How to Run the Application

### 1. Backend (Django)

```bash
# Apply database migrations
python manage.py migrate

# Run the Django development server
python manage.py runserver 8000
```

The backend will be live at `http://127.0.0.1:8000/`.

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

The frontend will be live at `http://localhost:5173/`.

---

## Running Automated Tests

Run the full Django test suite:

```bash
python manage.py test evaluator
```

---

## API Reference

### 1. Evaluate Prompt & Generate Synthetic Dataset
- **Method**: `POST`
- **Endpoint**: `/api/evaluate/`
- **Request Body**:
```json
{
  "department": "software",
  "task_type": "create content",
  "prompt": "Create technical documentation for a JWT authentication system using Node.js and Express.",
  "dataset_size": 20
}
```
- **Response**: Full JSON containing 15-dimension scores, synthetic dataset with 20 test cases, improved prompt, re-evaluation, and delta comparison.

### 2. List Evaluation History
- **Method**: `GET`
- **Endpoint**: `/api/evaluations/`

### 3. Get Evaluation Detail
- **Method**: `GET`
- **Endpoint**: `/api/evaluations/<id>/`

### 4. Download Excel Report
- **Method**: `GET`
- **Endpoint**: `/api/evaluations/<id>/export-excel/`

---

## Example Generated Synthetic Dataset Case

```json
{
  "prompt_id": "PROMPT-A1B2C3",
  "test_case_id": "TC-001",
  "input": "Create JWT authentication documentation focusing on secret key management, token generation, and Authorization Bearer header extraction in Express middleware.",
  "expected_output": "Markdown documentation outlining jwt.sign() usage, process.env.JWT_SECRET storage, and req.headers.authorization parsing with 401 Unauthorized handling.",
  "difficulty": "Easy",
  "category": "Authentication Flow",
  "edge_case": false,
  "notes": "Baseline verification of JWT generation and middleware parsing."
}
```

---

## Agent System Prompts Documentation

For the complete, verbatim system prompts and output schemas for all agents in the pipeline, see [`SYSTEM_PROMPTS.md`](./SYSTEM_PROMPTS.md):
- **Semantic & Requirements Analyzer Agent**
- **15-Dimension Prompt Evaluation Agent**
- **Synthetic Dataset Generation Agent**
- **Prompt Optimizer & Reconstruction Agent (Improver)**
- **Independent Re-Validator Agent**
