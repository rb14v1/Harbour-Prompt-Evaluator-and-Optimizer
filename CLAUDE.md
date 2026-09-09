# Prompt Evaluator and Optimizer

Automated system for evaluating and iteratively improving AI prompts through multi-agent orchestration. Takes user prompts as input and returns optimized versions with quality scores across 8 validation dimensions.

## Project Purpose

This system helps evaluate prompt quality systematically and suggest improvements when scores fall below a threshold (7.0). It uses specialized agents to classify, analyze, validate, and optimize prompts in an iterative loop (max 3 iterations).

## System Architecture

### Main Processing Pipeline

```
User Prompt
    ↓
1. Preprocessor Agent (normalize, structure)
    ↓
2. Classifier Agent (categorize, assess complexity)
    ↓
3. Analyzer Agent (decompose, extract components)
    ↓
4. Validator Agent (evaluate across 8 dimensions)
    ↓
5. Scoring Engine (calculate numerical scores)
    ↓
6. Report Agent or Improver Agent
    ├─ Score ≥ 7.0? → Report Agent (output final result)
    └─ Score < 7.0? → Improver Agent (rewrite) → loop back to Validator
```

Maximum 3 improvement iterations before returning final result.

## Core Agents

### 1. Preprocessor Agent
**Input:** Raw natural language prompt  
**Responsibilities:**
- Normalize text (whitespace, case consistency)
- Preserve original prompt verbatim
- Convert to structured format with metadata
- Extract basic prompt metadata (ID, length, timestamp)

**Output Format:**
```json
{
  "prompt_id": "unique_id",
  "original_prompt": "...",
  "processed_prompt": "...",
  "metadata": {
    "length": 123,
    "timestamp": "2026-09-09T...",
    "version": 1
  }
}
```

### 2. Classifier Agent
**Input:** Processed prompt  
**Responsibilities:**
- Detect prompt task type (from 9 categories below)
- Determine complexity level (Simple / Moderate / Complex)
- Generate confidence score (0.0–1.0)
- Validate against known task patterns

**Output Format:**
```json
{
  "task_type": "category_name",
  "complexity": "Moderate",
  "confidence": 0.94,
  "reasoning": "..."
}
```

### 3. Analyzer Agent
**Input:** Classified prompt  
**Responsibilities:**
- Decompose prompt into key components
- Extract intent, requirements, context, constraints
- Identify missing information and ambiguities
- Suggest areas for clarification
- Recommend expected output format

**Output Format:**
```json
{
  "intent": "primary goal",
  "requirements": ["req1", "req2"],
  "context": ["context1"],
  "constraints": ["constraint1"],
  "expected_output": "format/type",
  "missing_information": ["gap1"],
  "ambiguities": ["ambiguity1"]
}
```

### 4. Validator Agent
**Input:** Analysis results  
**Responsibilities:**
- Evaluate prompt across 8 validation dimensions
- Rate each dimension (Poor / Moderate / Good / Excellent)
- Provide evidence for ratings with examples
- Identify specific issues per dimension
- Highlight improvement targets
- Retrieve relevant examples from validation reference dataset

**Output Format:**
```json
{
  "validation": {
    "clarity": {
      "level": "Good",
      "score": 7.5,
      "issues": [],
      "evidence": "..."
    },
    "specificity": {...},
    "context": {...},
    "completeness": {...},
    "requirements": {...},
    "constraints": {...},
    "expected_output": {...},
    "actionability": {...}
  },
  "overall_issues": [...],
  "improvement_targets": [...]
}
```

### 5. Scoring Engine
**Input:** Validation results  
**Responsibilities:**
- Convert qualitative levels to numerical scores (see Scoring Mapping below)
- Calculate weighted scores per dimension
- Compute overall prompt score
- Compare against threshold (7.0)
- Identify underperforming dimensions
- Provide score breakdown

**Output Format:**
```json
{
  "dimension_scores": {
    "clarity": 7.5,
    "specificity": 5.0,
    "context": 7.5,
    "completeness": 7.5,
    "requirements": 5.0,
    "constraints": 7.5,
    "expected_output": 7.5,
    "actionability": 5.0
  },
  "overall_score": 6.56,
  "threshold": 7.0,
  "status": "Needs Improvement",
  "low_scoring_dimensions": ["specificity", "requirements", "actionability"]
}
```

### 6a. Improver Agent (Optimization Loop)
**Input:** Analysis, validation, and scoring results  
**Triggered:** When overall_score < 7.0  
**Responsibilities:**
- Rewrite prompt addressing identified weaknesses
- Preserve original intent and core meaning
- Focus on low-scoring dimensions first
- Apply structural and clarity improvements
- Document changes made

**Output Format:**
```json
{
  "improved_prompt": "revised version",
  "changes_made": [
    "added specificity about output format",
    "clarified context with examples"
  ],
  "dimensions_addressed": ["specificity", "requirements"],
  "intent_preserved": true,
  "iteration": 1
}
```

**Loop Control:**
- Maximum 3 iterations
- Each iteration: Improver → Validator → Scoring Engine
- Stop if: overall_score ≥ 7.0 OR iterations == 3
- Return improved prompt and full history

### 6b. Report Agent (Final Output)
**Input:** Complete evaluation/optimization history  
**Triggered:** When overall_score ≥ 7.0 OR max iterations reached  
**Responsibilities:**
- Aggregate all results across pipeline
- Synthesize original and improved (if applicable) prompts
- Display classification, analysis, validation results
- Show score progression across iterations
- Provide final status and summary recommendation

**Output Format:**
```json
{
  "original_prompt": "...",
  "classification": {...},
  "analysis": {...},
  "initial_evaluation": {...},
  "improvement_history": [
    {
      "iteration": 1,
      "improved_prompt": "...",
      "changes": [...],
      "evaluation": {...}
    }
  ],
  "final_evaluation": {...},
  "final_score": 7.5,
  "summary": "Prompt is now ready for use. Clarity improved significantly.",
  "status": "Ready"
}
```

## Task Categories (9 Types)

Classifier assigns each prompt to exactly one category:

1. **Create Content** – Generate text, documents, blog posts, etc.
2. **Create Code** – Write, refactor, or generate source code
3. **Research** – Gather and synthesize information (brief scope)
4. **Deep Research / Analysis** – Extended investigation, detailed synthesis
5. **Plan and Organize** – Structure projects, create outlines, schedules
6. **Ideate** – Brainstorm concepts, generate ideas
7. **Summarize** – Condense existing information
8. **Explain** – Teach concepts, clarify topics
9. **Optimize** – Improve performance, efficiency, clarity of existing work

## Validation Dimensions (8)

Validator assesses each prompt across these dimensions:

1. **Clarity** – Is the request unambiguous and easy to understand?
2. **Specificity** – Is enough detail provided to guide accurate execution?
3. **Context** – Is relevant background information included?
4. **Completeness** – Are all necessary information components present?
5. **Requirements** – Are success criteria and expectations explicit?
6. **Constraints** – Are limitations or boundaries defined?
7. **Expected Output** – Is the desired output format/structure clear?
8. **Actionability** – Can the prompt be executed immediately as written?

## Scoring System

### Quality Level Mapping

| Level | Score | Meaning |
|-------|-------|---------|
| Poor | 2.5 | Major gaps; needs substantial revision |
| Moderate | 5.0 | Some issues; would benefit from improvement |
| Good | 7.5 | Solid; minor refinements possible |
| Excellent | 10.0 | Exemplary; ready to use |

### Threshold

- **Overall Score ≥ 7.0** – Prompt passes; report generated
- **Overall Score < 7.0** – Prompt fails; improvement cycle triggered

### Calculation

Dimension scores (2.5–10.0) are averaged to compute overall score. Weighting by dimension can be applied (currently unweighted average).

## Datasets

### 1. Classification Dataset
- **Purpose:** Train/evaluate Classifier agent
- **Size:** 100–300 labeled examples
- **Content:** Prompts labeled with correct task category and complexity
- **Usage:** Validation of Classifier accuracy

### 2. Validation Reference Dataset
- **Purpose:** Support Validator agent with in-context examples
- **Size:** 160 examples (8 dimensions × 4 quality levels × 5 examples)
- **Content:** Example prompts rated across each dimension at each quality level
- **Usage:** Retrieved during validation to inform dimension scoring and evidence selection

### 3. Benchmark Dataset
- **Purpose:** End-to-end system evaluation
- **Size:** 100–200 unseen prompts
- **Content:** Complete prompts with ground-truth scores and improvement targets
- **Usage:** Assess overall system performance, precision, and recall

### 4. Improvement Dataset (Optional)
- **Purpose:** Evaluate Improver agent quality
- **Size:** 50–100 pairs of original and improved prompts
- **Content:** Real prompts before/after improvement with change annotations
- **Usage:** Measure intent preservation and improvement effectiveness

## Key Implementation Notes

### Data Flow
- Each agent receives structured input from previous agent
- Validation reference dataset is retrieved by Classifier output (task type)
- Original prompt preserved through entire pipeline for final report
- Metadata tracked at each stage (iteration count, timestamp, agent name)

### Iteration Control
- Counter incremented after each Improver run
- Maximum 3 iterations hard limit
- Early exit if score ≥ 7.0 at any point
- All improvement attempts and scores returned in final report

### Intent Preservation
- Improver must explicitly confirm intent_preserved: true
- Original intent checked against improved prompt by Validator
- If intent lost, that iteration flagged for review

### Error Handling
- Invalid task classification → return error with confidence < 0.5
- Incomplete analysis → flag missing components, retry Analyzer
- Score calculation errors → validate dimension scores before averaging
- Agent failures → log error, provide partial results, suggest manual review

## Development Guidelines

### Adding New Task Categories
1. Update Classifier dataset with ~20–30 labeled examples of new category
2. Add category to allowed categories list in Classifier agent
3. Update Analyzer with category-specific context patterns
4. Test with Classification Dataset evaluation

### Adding New Validation Dimensions
1. Add dimension to Validation Dimensions list (max 10 recommended)
2. Create 20 examples per quality level (4 levels × 20 = 80 new examples)
3. Update Validator agent prompt/validation logic
4. Update scoring calculation to include new dimension
5. Retest on Benchmark Dataset to ensure no regression

### Testing the Pipeline
- Unit test each agent independently with representative inputs
- Integration test with Benchmark Dataset prompts
- Track precision/recall on Classification Dataset
- Measure improvement effectiveness on Improvement Dataset
- Monitor end-to-end latency and iteration counts

### Code Organization
- Agents: Separate module/class per agent
- Datasets: Stored as JSON/CSV, loaded at startup
- Scoring logic: Centralized Scoring Engine module
- Report generation: Report Agent templates
- Config: Threshold, max iterations, dataset paths centralized

## Common Workflows

### Evaluate a Single Prompt
1. Preprocess → Classify → Analyze → Validate → Score
2. If score ≥ 7.0: Report Agent generates final output
3. Else: Improver Agent rewrites, loop until threshold or max iterations

### Batch Evaluate Prompts
- Process each prompt through pipeline sequentially
- Aggregate scores for statistical analysis
- Flag prompts in each category with lowest/highest scores
- Generate improvement recommendations for low-scoring batch

### Benchmark System Performance
1. Load Benchmark Dataset (100–200 prompts with ground-truth scores)
2. Run full pipeline on each prompt
3. Compare predicted scores vs. ground-truth
4. Calculate precision, recall, F1 across categories and dimensions
5. Generate performance report

### Continuous Improvement
1. Collect user feedback on generated improvement suggestions
2. Update Validation Reference Dataset with new examples
3. Retrain/adjust Validator agent on new patterns
4. Retest on Benchmark Dataset
5. Deploy updated system

## External Dependencies

- **Agent Framework:** Claude API with multi-agent support (or equivalent)
- **Data Storage:** JSON/CSV file loading (or database connection)
- **LLM Model:** Claude 3+ (or configured LLM) for all agents
- **Optional:** Web interface for prompt input/output display

## Future Enhancements

- Weighted dimension scoring (e.g., Specificity = 1.5×, Context = 0.8×)
- User-driven dimension priorities (customize for specific use cases)
- A/B testing framework for improvement suggestions
- Multi-language support for prompt evaluation
- Hybrid approach combining rule-based + LLM validation
- Integration with prompt management platforms
