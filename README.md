# Prompt Evaluator and Optimizer

Automated system for evaluating and iteratively improving AI prompts. This tool analyzes prompts across 8 quality dimensions, assigns a score, and automatically suggests improvements until your prompt meets the quality threshold.

## Features

- **Multi-Dimension Evaluation** – Assesses prompts across 8 key dimensions: clarity, specificity, context, completeness, requirements, constraints, expected output, and actionability
- **Automated Classification** – Categorizes prompts into 9 task types (Create Content, Create Code, Research, Deep Research, Plan & Organize, Ideate, Summarize, Explain, Optimize)
- **Complexity Assessment** – Determines task complexity (Simple, Moderate, Complex) and confidence score
- **Iterative Optimization** – Automatically rewrites weak prompts, up to 3 iterations, to reach a quality threshold of 7.0
- **Detailed Reporting** – Provides comprehensive evaluation reports with scores, issues identified, and improvement history
- **Intent Preservation** – Ensures prompt improvements maintain the original intent and meaning

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd prompt-evaluator-and-optimizer

# Install dependencies
npm install
# or
pip install -r requirements.txt
```

### Basic Usage

```bash
# Evaluate a prompt
node evaluate.js "Your prompt here"

# Or use the interactive mode
node evaluate.js --interactive
```

### Example

**Input Prompt:**
```
Create a function that sorts an array
```

**Output:**
```json
{
  "original_prompt": "Create a function that sorts an array",
  "classification": {
    "task_type": "Create Code",
    "complexity": "Simple",
    "confidence": 0.92
  },
  "initial_evaluation": {
    "dimension_scores": {
      "clarity": 7.5,
      "specificity": 2.5,
      "context": 2.5,
      "completeness": 2.5,
      "requirements": 2.5,
      "constraints": 2.5,
      "expected_output": 5.0,
      "actionability": 5.0
    },
    "overall_score": 4.06,
    "status": "Needs Improvement"
  },
  "improvement_history": [
    {
      "iteration": 1,
      "improved_prompt": "Create a Python function named 'sort_array' that takes a list of integers as input and returns them sorted in ascending order. Use a comparison-based sorting algorithm. Include docstring with parameters and return type.",
      "changes_made": [
        "Specified language (Python)",
        "Named the function",
        "Defined input type and format",
        "Specified output order (ascending)",
        "Requested algorithm approach",
        "Requested documentation"
      ],
      "evaluation": {
        "overall_score": 7.8,
        "status": "Ready"
      }
    }
  ],
  "final_score": 7.8,
  "summary": "Prompt was significantly improved. Added language specification, function naming, type information, and documentation requirements. Original intent preserved.",
  "status": "Ready"
}
```

## How It Works

### Processing Pipeline

1. **Preprocessor** – Normalizes input, preserves original prompt, structures metadata
2. **Classifier** – Categorizes task type and assesses complexity
3. **Analyzer** – Decomposes prompt into components (intent, requirements, constraints, context)
4. **Validator** – Evaluates across 8 dimensions, identifies issues and improvement targets
5. **Scoring Engine** – Converts qualitative ratings to numerical scores, compares against threshold
6. **Decision Point** – Score ≥ 7.0? Report final results : Improve prompt
7. **Improver** (if needed) – Rewrites prompt addressing weak dimensions, preserving intent
8. **Report** – Aggregates all results and returns comprehensive evaluation

See [CLAUDE.md](CLAUDE.md) for detailed technical architecture.

## Evaluation Dimensions

Each prompt is scored on these 8 dimensions (scale: 2.5 to 10.0):

| Dimension | Description |
|-----------|-------------|
| **Clarity** | Is the request unambiguous and easy to understand? |
| **Specificity** | Is enough detail provided to guide accurate execution? |
| **Context** | Is relevant background information included? |
| **Completeness** | Are all necessary information components present? |
| **Requirements** | Are success criteria and expectations explicit? |
| **Constraints** | Are limitations or boundaries defined? |
| **Expected Output** | Is the desired output format/structure clear? |
| **Actionability** | Can the prompt be executed immediately as written? |

### Quality Levels

- **2.5 (Poor)** – Major gaps; needs substantial revision
- **5.0 (Moderate)** – Some issues; would benefit from improvement
- **7.5 (Good)** – Solid; minor refinements possible
- **10.0 (Excellent)** – Exemplary; ready to use

**Threshold:** 7.0 (average across all dimensions)

## Task Categories

The system classifies prompts into these 9 categories:

1. Create Content
2. Create Code
3. Research
4. Deep Research / Analysis
5. Plan and Organize
6. Ideate
7. Summarize
8. Explain
9. Optimize

## Datasets

The system uses 4 datasets for training and evaluation:

1. **Classification Dataset** (100–300 examples) – Train Classifier accuracy
2. **Validation Reference Dataset** (160 examples) – Support Validator with quality examples
3. **Benchmark Dataset** (100–200 examples) – Evaluate end-to-end system performance
4. **Improvement Dataset** (50–100 pairs) – Measure improvement effectiveness

See data/ directory for dataset files.

## Project Structure

```
prompt-evaluator-and-optimizer/
├── README.md                          # This file
├── CLAUDE.md                          # Technical architecture & implementation guide
├── src/
│   ├── agents/
│   │   ├── preprocessor.js           # Normalize and structure prompts
│   │   ├── classifier.js             # Categorize and assess complexity
│   │   ├── analyzer.js               # Decompose prompt components
│   │   ├── validator.js              # Evaluate across 8 dimensions
│   │   ├── scoring-engine.js         # Calculate numerical scores
│   │   ├── improver.js               # Rewrite weak prompts
│   │   └── report.js                 # Generate final reports
│   ├── orchestrator.js               # Main pipeline controller
│   └── utils/
│       ├── config.js                 # Configuration & constants
│       └── logger.js                 # Logging utilities
├── data/
│   ├── classification-dataset.json    # Task categories & examples
│   ├── validation-reference.json      # Quality dimension examples
│   ├── benchmark-dataset.json         # Unseen test prompts
│   └── improvement-dataset.json       # Before/after improvement pairs
├── tests/
│   ├── agents/                        # Unit tests for each agent
│   ├── integration/                   # End-to-end pipeline tests
│   └── fixtures/                      # Test data and expected outputs
├── scripts/
│   ├── evaluate.js                    # CLI entry point
│   ├── batch-evaluate.js              # Process multiple prompts
│   └── benchmark.js                   # Run system benchmarks
└── package.json
```

## Command Reference

### Evaluate Single Prompt

```bash
node scripts/evaluate.js "Your prompt here"
```

**Options:**
- `--interactive` – Start interactive prompt input mode
- `--output json` – Output as JSON (default)
- `--output pretty` – Human-readable format
- `--save <path>` – Save results to file

### Batch Evaluation

```bash
node scripts/batch-evaluate.js <input-file> --output <output-file>
```

Process multiple prompts from CSV/JSON file.

### Run Benchmarks

```bash
node scripts/benchmark.js --dataset benchmark
```

Evaluate system performance on benchmark dataset. Outputs precision, recall, F1 scores.

### Interactive Mode

```bash
node scripts/evaluate.js --interactive
```

- Enter prompts interactively
- See real-time evaluation results
- Compare multiple prompts
- Export results

## Configuration

Edit `src/utils/config.js` to customize:

- **THRESHOLD** – Score required to pass (default: 7.0)
- **MAX_ITERATIONS** – Maximum improvement attempts (default: 3)
- **DATASET_PATHS** – Location of data files
- **QUALITY_LEVELS** – Score mappings (Poor/Moderate/Good/Excellent)
- **TASK_CATEGORIES** – Allowed prompt categories

## API Usage

### Python

```python
from prompt_optimizer import PromptEvaluator

evaluator = PromptEvaluator()
result = evaluator.evaluate("Your prompt here")

print(f"Score: {result['final_score']}")
print(f"Status: {result['status']}")
print(f"Improved Prompt: {result['final_prompt']}")
```

### JavaScript

```javascript
const { PromptEvaluator } = require('./src/orchestrator');

const evaluator = new PromptEvaluator();
const result = await evaluator.evaluate("Your prompt here");

console.log(`Score: ${result.final_score}`);
console.log(`Status: ${result.status}`);
console.log(`Improved Prompt: ${result.final_prompt}`);
```

## Performance

- **Single Prompt Evaluation:** ~2–5 seconds (depending on LLM latency)
- **Batch Processing:** ~100 prompts per minute
- **Improvement Cycle:** ~5–10 seconds per iteration
- **System Accuracy:** Varies by category (see benchmark results)

## Testing

```bash
# Run all tests
npm test

# Run specific test suite
npm test -- agents/classifier
npm test -- integration/pipeline

# Run with coverage
npm test -- --coverage

# Run benchmarks
npm run benchmark
```

## Contributing

1. Create a feature branch from `main`
2. Implement changes following project structure
3. Add tests for new agents or dimensions
4. Update CLAUDE.md if adding categories/dimensions
5. Run full test suite and benchmarks
6. Submit pull request with description of changes

### Adding New Task Categories

See "Adding New Task Categories" in [CLAUDE.md](CLAUDE.md#adding-new-task-categories).

### Adding New Validation Dimensions

See "Adding New Validation Dimensions" in [CLAUDE.md](CLAUDE.md#adding-new-validation-dimensions).

## Troubleshooting

### Low Scores on All Prompts
- Verify Validator agent is loading validation reference dataset
- Check that dimension weights are reasonable
- Run benchmark to see if issue is systematic

### Improver Not Making Progress
- Ensure intent_preserved flag is being validated
- Check that low-scoring dimensions are being targeted
- Review improvement history for patterns in failed iterations

### Classification Confidence Low
- Verify classification dataset is loaded
- Add more examples for that task category
- Check if prompt is ambiguous between categories

### Out of Memory on Large Batches
- Process in smaller batches
- Clear intermediate results after each prompt
- Use streaming output instead of in-memory aggregation

## Related Documentation

- **[CLAUDE.md](CLAUDE.md)** – Complete technical architecture, agents, datasets, and implementation guide
- **[data/README.md](data/README.md)** – Dataset format specifications and loading instructions
- **[tests/README.md](tests/README.md)** – Testing framework and guidelines

## License

[Add your license here]

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Review [CLAUDE.md](CLAUDE.md) for technical details
- Check test files for usage examples

## Roadmap

- [ ] Multi-language prompt evaluation
- [ ] Weighted dimension scoring by category
- [ ] User-driven dimension priorities
- [ ] A/B testing framework for improvements
- [ ] Web UI for interactive evaluation
- [ ] Integration with prompt management platforms
- [ ] Advanced intent preservation validation
- [ ] Custom dimension templates

---

**Last Updated:** 2026-09-09  
**Version:** 1.0.0
