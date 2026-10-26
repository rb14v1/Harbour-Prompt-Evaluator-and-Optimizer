# API Reference

## Base URL

```
http://127.0.0.1:8000/api/
```

## Endpoints

### 1. Evaluate Prompt

**POST** `/evaluate/`

Evaluates a prompt across 15 dimensions and generates synthetic test dataset.

#### Request

```json
{
  "department": "string (1-100 chars)",
  "task_type": "string (1-100 chars)",
  "prompt": "string (5-10000 chars)",
  "dataset_size": "integer (1-100, default: 5)",
  "prompt_id": "string (optional, max 50 chars)"
}
```

#### Response (Success: 200 OK)

```json
{
  "id": 1,
  "prompt_id": "PROMPT-ABC123",
  "department": "software",
  "task_type": "create documentation",
  "original_prompt": "Create JWT authentication documentation...",
  "processed_prompt": "Create JWT authentication documentation...",
  "analysis": {
    "prompt_intent": "Create comprehensive JWT documentation",
    "user_objective": "Generate technical documentation",
    "explicit_requirements": [
      "Document JWT generation",
      "Explain token validation"
    ],
    "implicit_requirements": [...],
    "context": "Software development JWT authentication",
    "target_audience": "Software developers",
    "expected_output": "Comprehensive documentation",
    "output_format": "Markdown Document",
    "constraints": [...],
    "dependencies": [...],
    "missing_information": [...],
    "ambiguities": [...],
    "potential_failure_modes": [...],
    "risks": [...],
    "edge_cases": [...],
    "complexity": "Medium",
    "important_assumptions": [...]
  },
  "evaluation": {
    "dimensions": {
      "instruction_following": {
        "name": "Instruction Following",
        "score": 7,
        "reasoning": "Clear directives provided",
        "identified_issue": "Lacks step-by-step breakdown",
        "recommendation": "Add numbered instructions"
      },
      ...
    },
    "overall_score": 6.5,
    "summary": "Prompt evaluated..."
  },
  "synthetic_dataset": {
    "dataset_size": 5,
    "test_cases": [
      {
        "prompt_id": "PROMPT-ABC123",
        "test_case_id": "TC-001",
        "input": "Standard software scenario...",
        "expected_output": "Clear, properly formatted...",
        "difficulty": "Easy",
        "category": "Authentication Flow",
        "notes": "Baseline validation...",
        "edge_case": false
      },
      ...
    ],
    "validation_summary": {
      "is_valid": true,
      "total_cases_validated": 5,
      "difficulty_distribution": {
        "Easy": 2,
        "Medium": 2,
        "Hard": 1
      },
      "category_distribution": {...},
      "edge_cases_count": 1,
      "issues_detected_and_repaired": [],
      "validation_status": "Passed"
    }
  },
  "improved_prompt": "<role>\nYou are an expert...\n</role>\n\n<instructions>...",
  "improvement_metadata": {
    "explanation_of_changes": [
      "Added modular role structure",
      "Defined explicit output schema",
      "Included edge case handling"
    ],
    "structural_sections_added": [
      "Role & Context",
      "Step-by-Step Instructions",
      "Output Schema",
      "Constraints & Edge Cases"
    ]
  },
  "re_evaluation": {
    "dimensions": {...},
    "overall_score": 7.8,
    "summary": "Re-evaluation shows improvement..."
  },
  "comparison": {
    "dimension_improvements": {
      "instruction_following": 1.5,
      "clarity": 1.2,
      ...
    },
    "overall_difference": 1.3,
    "improved_dimensions": [
      "instruction_following",
      "clarity"
    ],
    "unchanged_dimensions": [...],
    "regressed_dimensions": [],
    "key_insights": [
      "Structured format improved clarity significantly"
    ]
  },
  "overall_original_score": 6.5,
  "overall_improved_score": 7.8,
  "score_difference": 1.3,
  "status": "COMPLETED"
}
```

#### Response (Validation Error: 400 Bad Request)

```json
{
  "error": "Invalid request",
  "details": {
    "prompt": "ensure this value has at least 5 characters"
  }
}
```

#### Response (Server Error: 500 Internal Server Error)

```json
{
  "error": "An unexpected error occurred. Please check logs for details."
}
```

#### Example cURL

```bash
curl -X POST http://127.0.0.1:8000/api/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "department": "software",
    "task_type": "create documentation",
    "prompt": "Create comprehensive JWT authentication documentation for Node.js Express",
    "dataset_size": 5
  }'
```

#### Example Python

```python
import requests

response = requests.post(
    'http://127.0.0.1:8000/api/evaluate/',
    json={
        'department': 'software',
        'task_type': 'create documentation',
        'prompt': 'Create JWT authentication documentation',
        'dataset_size': 5
    }
)
result = response.json()
print(result['overall_original_score'])  # 6.5
```

---

### 2. List Evaluations

**GET** `/evaluations/`

List all evaluations with pagination and filtering support.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max: 100) |
| `search` | string | - | Search in prompt_id, department, task_type |
| `ordering` | string | -created_at | Sort by: created_at, overall_original_score, score_difference |

#### Response (Success: 200 OK)

```json
{
  "count": 42,
  "next": "http://127.0.0.1:8000/api/evaluations/?page=2",
  "previous": null,
  "page_size": 20,
  "total_pages": 3,
  "results": [
    {
      "id": 1,
      "prompt_id": "PROMPT-ABC123",
      "department": "software",
      "task_type": "create documentation",
      "original_prompt": "Create JWT...",
      "overall_original_score": 6.5,
      "overall_improved_score": 7.8,
      "score_difference": 1.3,
      "created_at": "2026-10-01T12:30:45Z",
      ...
    },
    ...
  ]
}
```

#### Example cURL

```bash
# Get first page
curl http://127.0.0.1:8000/api/evaluations/?page=1&page_size=20

# Search
curl http://127.0.0.1:8000/api/evaluations/?search=jwt

# Sort by score improvement
curl "http://127.0.0.1:8000/api/evaluations/?ordering=-score_difference"
```

---

### 3. Get Evaluation Detail

**GET** `/evaluations/{id}/`

Get full details of a specific evaluation.

#### Response (Success: 200 OK)

```json
{
  "id": 1,
  "prompt_id": "PROMPT-ABC123",
  ... (full evaluation object as in endpoint #1)
}
```

#### Response (Not Found: 404)

```json
{
  "detail": "Not found."
}
```

#### Example cURL

```bash
curl http://127.0.0.1:8000/api/evaluations/1/
```

---

### 4. Export to Excel

**GET** `/evaluations/{id}/export-excel/`

Download Excel workbook containing evaluation report.

#### Response

Binary Excel file (.xlsx)

#### Headers

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="Prompt_Evaluation_PROMPT-ABC123.xlsx"
```

#### Example cURL

```bash
curl -o evaluation_report.xlsx \
  http://127.0.0.1:8000/api/evaluations/1/export-excel/
```

---

### 5. Direct Excel Export

**POST** `/export-excel/`

Export evaluation directly to Excel without saving to database.

#### Request

```json
{
  "prompt_id": "PROMPT-CUSTOM",
  "department": "software",
  "task_type": "create documentation",
  ... (full evaluation object)
}
```

#### Response

Binary Excel file (.xlsx)

#### Example cURL

```bash
curl -X POST http://127.0.0.1:8000/api/export-excel/ \
  -H "Content-Type: application/json" \
  -d @evaluation.json \
  -o report.xlsx
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Evaluation not found |
| 429 | Too Many Requests | Rate limit exceeded (60/min) |
| 500 | Internal Server Error | Unexpected server error |

### Error Response Format

```json
{
  "error": "Human-readable error message",
  "error_code": "VALIDATION_ERROR|LLM_ERROR|INTERNAL_ERROR",
  "details": {
    "field_name": "specific issue description"
  },
  "type": "user_error|system_error"
}
```

---

## Rate Limiting

- **Limit**: 60 requests per minute per IP address
- **Reset**: After 60 seconds

When limit exceeded:

```json
{
  "error": "Rate limit exceeded. Maximum 60 requests per minute.",
  "retry_after": 60
}
```

---

## Request Validation

All requests are validated with strict bounds:

| Field | Min | Max | Required |
|-------|-----|-----|----------|
| department | 1 | 100 | Yes |
| task_type | 1 | 100 | Yes |
| prompt | 5 | 10000 | Yes |
| dataset_size | 1 | 100 | No (default: 5) |
| prompt_id | - | 50 | No |

### Validation Example

```bash
# Invalid: prompt too short
curl -X POST http://127.0.0.1:8000/api/evaluate/ \
  -d '{"department": "test", "task_type": "test", "prompt": "Hi"}'

# Response 400:
{
  "error": "Invalid request",
  "details": {
    "prompt": "ensure this value has at least 5 characters"
  }
}
```

---

## Performance Tips

1. **Batch Processing**: Evaluations can take 3-8 seconds each
2. **Pagination**: Use small page sizes for large result sets
3. **Caching**: Results are cached for 5 minutes
4. **Async**: Consider making API calls asynchronously from frontend

---

## Webhook Support (Future)

Currently not implemented. Evaluation requests are synchronous.

---

## SDK/Library Support

- **Python**: Use `requests` library
- **JavaScript**: Use `fetch` or `axios`
- **cURL**: See examples above

---

## Changelog

### v1.0 (Current)
- Complete evaluation pipeline
- Synthetic dataset generation
- Excel export
- Pagination and filtering
- Rate limiting
- Validation
