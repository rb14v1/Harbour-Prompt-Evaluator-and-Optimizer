# Synthetic Datasets for Prompt Evaluator and Optimizer

This directory contains three comprehensive synthetic datasets designed to support the development, testing, and evaluation of the Prompt Evaluator and Optimizer system.

## Overview

| Dataset | File | Purpose | Examples | Dimensions |
|---------|------|---------|----------|-----------|
| Benchmark | `benchmark_dataset.json` | End-to-end system testing | 140 | Quality levels, complexity |
| Validation Reference | `validation_reference_dataset.json` | Agent training & testing | 160 | 8 dimensions × 4 quality levels |
| Classification | `classification_dataset.json` | Classifier agent training | 270 | 9 task categories × complexity |

---

## 1. Benchmark Dataset (`benchmark_dataset.json`)

### Purpose
End-to-end testing of the complete Prompt Evaluator and Optimizer pipeline. Tests all agents working together.

### Structure
```json
{
  "metadata": { /* version, creation date, stats */ },
  "examples": [
    {
      "id": "BCE001",
      "prompt": "User's original prompt",
      "task_type": "Create Content",
      "complexity": "Simple | Moderate | Complex",
      "expected_quality": "Poor | Moderate | Good | Excellent",
      "expected_score": 3.5,
      "issues": ["clarity issue", "missing specificity"],
      "low_dimensions": ["Clarity", "Specificity"]
    }
  ]
}
```

### Usage Examples

**1. Test Classifier Agent**
```python
from benchmark_dataset import load_benchmark_dataset

data = load_benchmark_dataset()
classifier_test_set = data['examples']

for example in classifier_test_set:
    predicted_type = classifier.classify(example['prompt'])
    assert predicted_type == example['task_type'], \
        f"Failed: {example['id']}"
```

**2. Test Validator Agent**
```python
for example in classifier_test_set:
    validation_result = validator.evaluate(example['prompt'])
    
    # Check that low_dimensions match expected issues
    assert set(validation_result['low_dimensions']) == \
           set(example['low_dimensions'])
```

**3. Test Full Pipeline**
```python
for example in classifier_test_set:
    final_report = pipeline.evaluate_and_optimize(example['prompt'])
    
    # Verify score improvement if needed optimization
    if example['expected_score'] < 7.0:
        assert final_report['final_evaluation']['overall_score'] >= 7.0
```

### Key Features
- **Diverse Coverage**: All 9 task categories represented
- **Complexity Range**: Simple (entry-level), Moderate (mid-level), Complex (advanced)
- **Quality Levels**: Poor (2.5), Moderate (5.0), Good (7.5), Excellent (10.0)
- **Expected Scores**: Ground truth for validation
- **Issue Labels**: Pre-identified problems for evaluation accuracy

---

## 2. Validation Reference Dataset (`validation_reference_dataset.json`)

### Purpose
Training and reference data for the Validator agent. Provides examples of each validation dimension at each quality level.

### Structure
```json
{
  "metadata": { /* dimensions, quality levels, stats */ },
  "examples": {
    "Clarity": {
      "Poor": [
        {
          "id": "CLR_P_001",
          "prompt": "Do something about the data.",
          "issue": "Vague language, no clear intent",
          "score": 2.5
        }
      ],
      "Moderate": [...],
      "Good": [...],
      "Excellent": [...]
    },
    "Specificity": { /* similar structure */ },
    // ... 6 more dimensions
  }
}
```

### Validation Dimensions

| Dimension | Focus | Example Poor | Example Excellent |
|-----------|-------|--------------|-------------------|
| **Clarity** | Unambiguous intent | "Do something" | "Write Python function that validates emails using RFC 5322" |
| **Specificity** | Detailed requirements | "Write content" | "2000-word blog post on transformers targeting software engineers" |
| **Context** | Business/domain context | "Build a system" | "Build payment API for e-commerce with PCI compliance" |
| **Completeness** | All needed information | "Optimize code" | "Optimize database with current 45s goal <15s metrics" |
| **Requirements** | Functional/non-functional specs | No input/output defined | Input/output, performance, scalability clearly specified |
| **Constraints** | Limitations & boundaries | None mentioned | Memory limits, deadline, team size, tech stack defined |
| **Expected Output** | Deliverable format | Vague output | Specific format: 2-page report with charts and metrics |
| **Actionability** | Clear next steps | No action items | Specific, measurable, implementable tasks defined |

### Usage Examples

**1. Validator Agent Training**
```python
from validation_reference_dataset import load_validation_data

# Load reference examples per dimension
clarity_examples = load_validation_data('Clarity')

# Use as training data or reference during evaluation
def evaluate_clarity(prompt, reference_examples=clarity_examples):
    # Compare prompt against reference examples
    for level, examples in reference_examples.items():
        for example in examples:
            if is_similar(prompt, example['prompt']):
                return level  # Return quality level
```

**2. In-Context Learning**
```python
# Use best examples for few-shot learning in Validator
validator_prompt = f"""
You are evaluating prompt quality on the Clarity dimension.

Here are examples:

Poor clarity:
{example_poor['prompt']}
Issue: {example_poor['issue']}
Score: {example_poor['score']}

Good clarity:
{example_good['prompt']}
Score: {example_good['score']}

Excellent clarity:
{example_excellent['prompt']}
Score: {example_excellent['score']}

Now evaluate this prompt: {user_prompt}
"""
```

**3. Benchmark Performance**
```python
# Create test set from reference data
test_examples = []
for dimension in DIMENSIONS:
    for quality_level in ['Poor', 'Moderate', 'Good', 'Excellent']:
        test_examples.extend(
            load_validation_data(dimension)[quality_level]
        )

# Test validator accuracy
correct = 0
for example in test_examples:
    predicted = validator.evaluate_dimension(
        example['prompt'], 
        dimension
    )
    if predicted['score'] == example['score']:
        correct += 1

accuracy = correct / len(test_examples)
```

### Quality Level Definitions

| Level | Score | Characteristics |
|-------|-------|-----------------|
| **Poor** | 2.5 | Vague, ambiguous, missing essential information, no actionable path |
| **Moderate** | 5.0 | Some clarity, but gaps in specificity, context, or completeness |
| **Good** | 7.5 | Clear intent, mostly specific, context provided, minor gaps |
| **Excellent** | 10.0 | Crystal clear, highly specific, complete context, fully actionable |

---

## 3. Classification Dataset (`classification_dataset.json`)

### Purpose
Training and evaluation of the Classifier agent for task type and complexity detection.

### Structure
```json
{
  "metadata": { /* categories, examples per category, stats */ },
  "task_categories": [
    {
      "name": "Create Content",
      "description": "Writing blogs, articles, social media posts...",
      "examples": [
        {
          "id": "CC001",
          "prompt": "Write a blog post about AI.",
          "complexity": "Simple | Moderate | Complex"
        }
      ]
    }
  ]
}
```

### Task Categories (9 Total)

| Category | Examples | Complexity Range |
|----------|----------|------------------|
| **Create Content** | Blog posts, newsletters, press releases, social media | Simple → Complex |
| **Create Code** | Functions, APIs, applications, algorithms | Simple → Complex |
| **Research** | Market research, literature review, trend analysis | Simple → Complex |
| **Deep Research / Analysis** | Comprehensive analysis, competitive analysis, strategic analysis | Simple → Complex |
| **Plan and Organize** | Project planning, roadmaps, scheduling, organizing | Simple → Complex |
| **Ideate** | Brainstorming, generating concepts, innovation | Simple → Complex |
| **Summarize** | Summaries, abstracts, condensing information | Simple → Complex |
| **Explain** | Explaining concepts, teaching, clarification | Simple → Complex |
| **Optimize** | Performance, efficiency, process improvements | Simple → Complex |

### Complexity Levels

| Level | Characteristics | Examples |
|-------|-----------------|----------|
| **Simple** | Single concept, minimal context, straightforward execution | "Write a blog post", "Write Python function" |
| **Moderate** | Multiple concepts, specific requirements, clear scope | "Write technical blog on ML for engineers", "Build REST API with JWT" |
| **Complex** | Multiple interconnected concepts, nuanced requirements, strategic scope | "Build distributed system with consensus algorithms", "Plan 24-month product roadmap" |

### Usage Examples

**1. Classifier Agent Training**
```python
from classification_dataset import load_classification_data

data = load_classification_data()
training_set = data['task_categories']

# Convert to training format
X_train = [example['prompt'] for category in training_set 
           for example in category['examples']]
y_train = [category['name'] for category in training_set 
           for example in category['examples']]

# Train classifier
classifier.train(X_train, y_train)
```

**2. Confidence Score Testing**
```python
# Test classifier on examples it should handle well
test_category = data['task_categories'][0]  # Create Content

for example in test_category['examples']:
    prediction, confidence = classifier.classify_with_confidence(
        example['prompt']
    )
    
    assert prediction == test_category['name']
    assert confidence > 0.85  # High confidence on clear examples
```

**3. Complexity Detection**
```python
# Test complexity classification
for category in data['task_categories']:
    simple_examples = [e for e in category['examples'] 
                       if e['complexity'] == 'Simple']
    complex_examples = [e for e in category['examples'] 
                        if e['complexity'] == 'Complex']
    
    for example in simple_examples:
        complexity = classifier.detect_complexity(example['prompt'])
        assert complexity == 'Simple'
    
    for example in complex_examples:
        complexity = classifier.detect_complexity(example['prompt'])
        assert complexity == 'Complex'
```

**4. Cross-category Testing**
```python
# Ensure classifier can distinguish between categories
category_pairs = [
    ('Create Content', 'Create Code'),
    ('Research', 'Deep Research / Analysis'),
    ('Ideate', 'Plan and Organize'),
]

for cat1, cat2 in category_pairs:
    examples_cat1 = [e['prompt'] for cat in data['task_categories'] 
                     if cat['name'] == cat1 for e in cat['examples']]
    examples_cat2 = [e['prompt'] for cat in data['task_categories'] 
                     if cat['name'] == cat2 for e in cat['examples']]
    
    predictions_cat1 = [classifier.classify(p) for p in examples_cat1]
    predictions_cat2 = [classifier.classify(p) for p in examples_cat2]
    
    # Calculate discrimination accuracy
    accuracy_cat1 = sum(1 for p in predictions_cat1 
                        if p == cat1) / len(predictions_cat1)
    accuracy_cat2 = sum(1 for p in predictions_cat2 
                        if p == cat2) / len(predictions_cat2)
```

---

## How to Use These Datasets

### Phase 1: Agent Development
1. Use **Classification Dataset** to train/test Classifier agent
2. Use **Validation Reference Dataset** to train/test Validator agent
3. Use **Benchmark Dataset** for integration testing

### Phase 2: System Evaluation
```python
# Load all datasets
benchmark = load_benchmark_dataset()
validation_ref = load_validation_reference_dataset()
classification = load_classification_dataset()

# Run comprehensive evaluation
results = {
    'classifier_accuracy': test_classifier(classification),
    'validator_accuracy': test_validator(validation_ref),
    'end_to_end_success_rate': test_pipeline(benchmark),
    'improvement_effectiveness': test_improvement_loop(benchmark),
}
```

### Phase 3: Performance Benchmarking
```python
# Measure system performance on benchmark dataset
metrics = {
    'avg_evaluation_time': measure_evaluation_speed(benchmark),
    'avg_improvement_iterations': measure_improvement_efficiency(benchmark),
    'score_improvement_rate': measure_score_gains(benchmark),
    'user_satisfaction': measure_prompt_quality_improvement(benchmark),
}
```

---

## Dataset Statistics

### Benchmark Dataset
- **Total Examples**: 140
- **Task Categories**: 9 (all covered)
- **Complexity Distribution**: ~33% Simple, ~50% Moderate, ~17% Complex
- **Quality Distribution**: ~25% Poor, ~25% Moderate, ~25% Good, ~25% Excellent
- **Score Range**: 1.5 - 9.2
- **Improvement Targets**: ~60% examples need optimization (score < 7.0)

### Validation Reference Dataset
- **Total Examples**: 160 (8 dimensions × 4 quality levels × 5 examples)
- **Dimensions**: 8 (Clarity, Specificity, Context, Completeness, Requirements, Constraints, Expected Output, Actionability)
- **Quality Levels**: 4 (Poor: 2.5, Moderate: 5.0, Good: 7.5, Excellent: 10.0)
- **Examples per Configuration**: 5

### Classification Dataset
- **Total Examples**: 270 (9 categories × 30 examples each)
- **Task Categories**: 9
- **Examples per Category**: 30
- **Complexity Distribution per Category**: 10 Simple, 10 Moderate, 10 Complex

---

## Loading Datasets in Python

```python
import json

def load_benchmark_dataset():
    with open('benchmark_dataset.json', 'r') as f:
        return json.load(f)

def load_validation_reference_dataset():
    with open('validation_reference_dataset.json', 'r') as f:
        return json.load(f)

def load_classification_dataset():
    with open('classification_dataset.json', 'r') as f:
        return json.load(f)

# Usage
benchmark = load_benchmark_dataset()
validation_ref = load_validation_reference_dataset()
classification = load_classification_dataset()
```

---

## Quality Assurance

All datasets have been generated with:
- ✅ Diverse, realistic examples
- ✅ Consistent quality levels
- ✅ Balanced category distribution
- ✅ Clear complexity progression
- ✅ Actionable validation dimensions
- ✅ Comprehensive task coverage

---

## Next Steps

1. **Integrate datasets** into your agent training pipeline
2. **Validate agent performance** using provided examples
3. **Iterate on agents** based on evaluation results
4. **Expand datasets** as you identify new edge cases
5. **Monitor improvements** over time with consistent benchmarks
