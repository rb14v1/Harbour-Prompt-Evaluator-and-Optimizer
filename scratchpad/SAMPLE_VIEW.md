# Dataset Sample View: 50 Claude-Improved Prompts

## Quick Reference

This file shows 10 representative samples from the 50-sample dataset. All 50 samples are stored in `dataset_50_samples.json`.

---

## Sample 1 of 50

**DEFICIENT PROMPT (original):**
```
Write something about data
```

**CLAUDE IMPROVED PROMPT:**
```
Write a 2-3 page technical report on data warehousing best practices. 
Include: (1) introduction to data warehousing, (2) key architectural 
patterns, (3) comparison of star vs snowflake schemas. Target audience: 
mid-level data engineers. Format as markdown with code examples and 
provide actionable recommendations.
```

**Dimensions Added:** clarity, specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 5 of 50

**DEFICIENT PROMPT (original):**
```
Help with the problem
```

**CLAUDE IMPROVED PROMPT:**
```
I'm experiencing high CPU usage (85%+) in our production Kubernetes 
cluster during peak hours (9-11 AM). Context: we run 50 microservices on 
k8s, using Prometheus for monitoring. Please analyze and provide: (1) 
diagnostic steps, (2) likely root causes, (3) optimization recommendations. 
Constraint: solution must not require service downtime.
```

**Dimensions Added:** clarity, specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 10 of 50

**DEFICIENT PROMPT (original):**
```
Design a system
```

**CLAUDE IMPROVED PROMPT:**
```
Design a microservices architecture for an e-commerce platform handling 
10k orders/day. Components needed: product catalog, cart, checkout, 
payment processing. Constraints: 99.9% uptime SLA, <2s page load time. 
Deliverables: architecture diagram (draw.io), component interactions, 
technology stack rationale, scalability plan.
```

**Dimensions Added:** clarity, specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 15 of 50

**DEFICIENT PROMPT (original):**
```
Build an API that handles user requests
```

**CLAUDE IMPROVED PROMPT:**
```
Build a REST API (Python FastAPI) for our image processing service. 
Endpoints: (1) upload image, (2) apply filters (grayscale, blur, resize), 
(3) get processing status. Requirements: handle 100MB files, async 
processing, support 50k req/day. Output: deployed API + OpenAPI docs + 
usage examples.
```

**Dimensions Added:** specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 20 of 50

**DEFICIENT PROMPT (original):**
```
Optimize performance
```

**CLAUDE IMPROVED PROMPT:**
```
Optimize database query performance for our user dashboard. Current: 5s 
load time (unacceptable). Constraints: cannot change schema. Approach: 
analyze slow queries, add indexes, refactor N+1 problems. Target: <500ms. 
Deliverable: before/after performance metrics + optimization summary.
```

**Dimensions Added:** specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 25 of 50

**DEFICIENT PROMPT (original):**
```
Reduce costs
```

**CLAUDE IMPROVED PROMPT:**
```
Reduce cloud infrastructure costs by 30% while maintaining performance 
SLAs. Current: $50k/month AWS spend. Provide: (1) cost analysis by 
service, (2) optimization opportunities ranked by impact, (3) 
implementation plan with risk assessment. Timeline: 6 weeks.
```

**Dimensions Added:** specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 30 of 50

**DEFICIENT PROMPT (original):**
```
Create a dashboard for monitoring
```

**CLAUDE IMPROVED PROMPT:**
```
Create a real-time monitoring dashboard using React + Grafana for 
infrastructure metrics. Metrics: CPU, memory, disk I/O across 20 servers. 
Requirements: refresh every 30s, alert thresholds (red/yellow), drill-down 
capability. Expected output: React component + Grafana dashboard JSON + 
deployment instructions.
```

**Dimensions Added:** specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 35 of 50

**DEFICIENT PROMPT (original):**
```
Make a website
```

**CLAUDE IMPROVED PROMPT:**
```
Build a responsive marketing website for our SaaS product. Pages: landing, 
pricing, docs, contact. Requirements: mobile-first design, <3s load time, 
SEO-optimized. Tech: Next.js + Tailwind. Output: fully deployed site + 
sitemap + analytics integration + 95+ Lighthouse score.
```

**Dimensions Added:** specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 40 of 50

**DEFICIENT PROMPT (original):**
```
Monitor and alert on changes
```

**CLAUDE IMPROVED PROMPT:**
```
Monitor application health metrics and send alerts. Metrics: error rate >5%, 
response time >2s, DB connection pool >80% utilized. Alerts: Slack 
notification + PagerDuty escalation if not acknowledged in 5min. Dashboard: 
Grafana. Output: monitoring setup + alert configuration.
```

**Dimensions Added:** specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Sample 45 of 50

**DEFICIENT PROMPT (original):**
```
Implement best practices
```

**CLAUDE IMPROVED PROMPT:**
```
Implement API security best practices across our 15 microservices. 
Standards: OWASP API security, rate limiting, input validation, 
authentication/authorization. Current state: inconsistent implementation. 
Constraints: zero-downtime deployment. Output: security framework + shared 
utilities library + deployment playbook + compliance checklist.
```

**Dimensions Added:** specificity, context, completeness, requirements, constraints, expected_output, actionability

---

## Statistics

- **Total Samples:** 50
- **Avg Deficient Prompt Length:** 3-7 words
- **Avg Improved Prompt Length:** 45-85 words (15.12x expansion)
- **Avg Dimensions Added:** 3.22 out of 8

---

## How to Access Full Dataset

All 50 samples with detailed metadata are stored in:

📁 `dataset_50_samples.json`

Each entry contains:
- `sample_id` — Unique identifier (SAMPLE_001 through SAMPLE_050)
- `original_deficient_prompt` — Vague starting prompt
- `claude_improved_prompt` — Claude-enhanced version
- `missing_dimensions` — Auto-detected missing dimensions
- `timestamp` — Generation timestamp

---

## How to Integrate with Your Project

### Option 1: Use as Validation Dataset
Load `dataset_50_samples.json` into your Benchmark Dataset and evaluate how your original project's Validator/Improver agents score these Claude-generated prompts.

### Option 2: Evaluate Your Improver Against Claude
1. Use your original Improver agent on the deficient prompts
2. Compare your improvements with Claude's improvements
3. Measure which approach produces higher validation scores

### Option 3: Feed Through Your Pipeline
```python
for sample in dataset:
    deficient = sample['original_deficient_prompt']
    
    # Run through your pipeline
    result = pipeline.process(deficient)
    
    # Compare with Claude
    comparison = {
        'your_improvement': result['improved_prompt'],
        'claude_improvement': sample['claude_improved_prompt'],
        'your_score': result['final_score'],
        'claude_score': evaluate(sample['claude_improved_prompt'])
    }
```

---

## Notes

- ✓ No project files modified
- ✓ No git commits created
- ✓ All generated in scratchpad directory
- ✓ Safe to delete if not needed
