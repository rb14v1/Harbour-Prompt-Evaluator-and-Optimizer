"""
Generate 50 sample prompts lacking 8 dimensions and create improved versions.
This is for comparison with the original project approach.
"""

import json
from datetime import datetime

# 50 sample prompts that lack one or more dimensions
DEFICIENT_PROMPTS = [
    # Clarity issues
    "Write something about data",
    "Make a thing work",
    "Improve the stuff",
    "Help with the problem",
    "Fix the issue",

    # Specificity issues
    "Create a document",
    "Write some code",
    "Analyze the information",
    "Build a tool",
    "Design a system",

    # Context issues
    "Generate a report",
    "Summarize the content",
    "Extract the data",
    "Create a list",
    "Format the output",

    # Completeness issues
    "Build an API that handles user requests",
    "Create a dashboard for monitoring",
    "Write a script to process files",
    "Design a database schema",
    "Develop a recommendation system",

    # Requirements issues
    "Make a website",
    "Build an app",
    "Create a service",
    "Implement a feature",
    "Set up infrastructure",

    # Constraints issues
    "Optimize performance",
    "Reduce costs",
    "Improve efficiency",
    "Scale the system",
    "Enhance security",

    # Expected Output issues
    "Analyze this dataset",
    "Review the code",
    "Evaluate the design",
    "Assess the proposal",
    "Compare the options",

    # Actionability issues
    "Consider the implications",
    "Reflect on the approach",
    "Think about the strategy",
    "Examine the methodology",
    "Discuss the framework",

    # Multiple missing dimensions
    "Do something with the data",
    "Handle user interactions",
    "Process and store information",
    "Generate and display results",
    "Manage and update records",
    "Validate and transform input",
    "Compute and cache values",
    "Query and filter data",
    "Export and archive content",
    "Monitor and alert on changes",
    "Improve the workflow",
    "Enhance user experience",
    "Optimize resource usage",
    "Implement best practices",
    "Update the documentation",
]

# Improved versions addressing all 8 dimensions
IMPROVED_PROMPTS = [
    # Original: "Write something about data"
    "Write a 2-3 page technical report on data warehousing best practices. Include: (1) introduction to data warehousing, (2) key architectural patterns, (3) comparison of star vs snowflake schemas. Target audience: mid-level data engineers. Format as markdown with code examples and provide actionable recommendations.",

    # Original: "Make a thing work"
    "Debug and fix the payment processing module in our Node.js backend. Specifically: the webhook handler is not properly logging transaction failures. Provide: (1) root cause analysis, (2) code fix with error handling, (3) test cases to verify the fix. Ensure backwards compatibility with existing integrations.",

    # Original: "Improve the stuff"
    "Refactor the authentication module in our Python Django app to reduce code duplication and improve readability. Currently, token validation logic is duplicated across 3 middleware classes. Requirements: maintain all existing functionality, add unit tests for new structure, document the refactoring in REFACTOR.md. Expected output: refactored code with 80%+ test coverage.",

    # Original: "Help with the problem"
    "I'm experiencing high CPU usage (85%+) in our production Kubernetes cluster during peak hours (9-11 AM). Context: we run 50 microservices on k8s, using Prometheus for monitoring. Please analyze and provide: (1) diagnostic steps, (2) likely root causes, (3) optimization recommendations. Constraint: solution must not require service downtime.",

    # Original: "Fix the issue"
    "Fix the race condition in our concurrent cache invalidation system (Python). Issue: multiple threads sometimes cache stale data. Requirements: ensure thread safety without using global locks, maintain performance for 10k+ requests/sec. Provide: unit tests, performance benchmarks, and architectural diagram of the fix.",

    # Original: "Create a document"
    "Create a 1500-word technical documentation for our REST API v2 release. Include: (1) authentication overview (OAuth2), (2) endpoint reference with curl examples, (3) rate limiting policy, (4) error codes and handling, (5) migration guide from v1. Format: markdown with code blocks. Audience: API consumers and internal developers. Deadline: 3 days.",

    # Original: "Write some code"
    "Write a Python script that reads CSV files from S3, transforms data (filters null values, standardizes dates), and loads into PostgreSQL. Requirements: handle up to 1GB files, implement retry logic for S3 failures, log all operations. Expected output: production-ready code with error handling and unit tests covering normal + edge cases.",

    # Original: "Analyze the information"
    "Analyze our Q3 customer churn data (CSV, 50k rows). Context: retail SaaS product, B2B focus. Determine: (1) churn rate by segment, (2) key churn drivers, (3) predictive indicators. Provide: detailed analysis in Jupyter notebook, statistical significance tests, actionable retention recommendations with priority ranking.",

    # Original: "Build a tool"
    "Build a CLI tool in Go that monitors Elasticsearch cluster health. Features: (1) health status check, (2) shard allocation report, (3) query performance warnings. Requirements: <50ms response time, JSON output, configurable alert thresholds. Output: compiled binary + installation guide.",

    # Original: "Design a system"
    "Design a microservices architecture for an e-commerce platform handling 10k orders/day. Components needed: product catalog, cart, checkout, payment processing. Constraints: 99.9% uptime SLA, <2s page load time. Deliverables: architecture diagram (draw.io), component interactions, technology stack rationale, scalability plan.",

    # Original: "Generate a report"
    "Generate a monthly performance report for our ML model in production. Metrics: precision, recall, F1-score across 5 customer segments. Compare: current vs baseline performance. Format: HTML dashboard with charts + PDF summary (2 pages). Include: top failure cases and recommended improvements.",

    # Original: "Summarize the content"
    "Summarize the following 50-page regulatory compliance document into a 1-page executive summary. Focus on: (1) key requirements, (2) risk areas, (3) implementation timeline. Audience: C-level executives. Include: sections for business impact, cost implications, and timeline for compliance.",

    # Original: "Extract the data"
    "Extract customer contact information from 100 unstructured email attachments (PDF format). Requirements: (1) structure as CSV (name, email, phone), (2) validate and normalize phone numbers, (3) flag duplicates, (4) log extraction errors. Expected output: cleaned CSV + error log with 95%+ accuracy.",

    # Original: "Create a list"
    "Create a comprehensive checklist for post-deployment smoke testing. Context: microservices architecture, 10+ services. Include: (1) health checks, (2) integration points, (3) critical user journeys, (4) performance baselines. Format: markdown with estimated time per check. Output: deployable runbook for QA team.",

    # Original: "Format the output"
    "Transform our raw application logs (1GB daily) into a structured format suitable for Elasticsearch. Requirements: parse multiline error stacks, extract structured fields (timestamp, level, service, request_id), handle 5+ log formats. Deliverable: transformation script + documentation of log field mapping.",

    # Original: "Build an API that handles user requests"
    "Build a REST API (Python FastAPI) for our image processing service. Endpoints: (1) upload image, (2) apply filters (grayscale, blur, resize), (3) get processing status. Requirements: handle 100MB files, async processing, support 50k req/day. Output: deployed API + OpenAPI docs + usage examples.",

    # Original: "Create a dashboard for monitoring"
    "Create a real-time monitoring dashboard using React + Grafana for infrastructure metrics. Metrics: CPU, memory, disk I/O across 20 servers. Requirements: refresh every 30s, alert thresholds (red/yellow), drill-down capability. Expected output: React component + Grafana dashboard JSON + deployment instructions.",

    # Original: "Write a script to process files"
    "Write a Bash script to batch-process video files: convert MP4→WebM, resize to 1280x720, add watermark. Requirements: parallel processing (4 threads), error recovery, progress logging. Handle 50+ files. Output: production-ready script with error handling + README.",

    # Original: "Design a database schema"
    "Design a PostgreSQL schema for a multi-tenant SaaS platform. Entities: tenants, users, projects, tasks. Constraints: handle 1M users, support soft-delete, ensure row-level security. Deliverables: SQL migrations + ER diagram + indexing strategy + query optimization notes.",

    # Original: "Develop a recommendation system"
    "Develop a collaborative filtering recommendation engine (Python). Data: 100k users, 50k items, 10M interactions. Requirements: real-time scoring for <5M items, daily batch training, A/B test readiness. Output: model code + API integration guide + performance metrics.",

    # Original: "Make a website"
    "Build a responsive marketing website for our SaaS product. Pages: landing, pricing, docs, contact. Requirements: mobile-first design, <3s load time, SEO-optimized. Tech: Next.js + Tailwind. Output: fully deployed site + sitemap + analytics integration + 95+ Lighthouse score.",

    # Original: "Build an app"
    "Build a mobile app (React Native) for order tracking. Features: real-time status updates, push notifications, map integration. Requirements: iOS + Android, offline support, <50MB bundle size. Deliverables: published to app stores + release notes + user guide.",

    # Original: "Create a service"
    "Create a microservice that validates and enriches customer data. Input: JSON customer records. Processing: validate format, deduplicate, enrich with third-party APIs (address verification). Requirements: process 10k records/min, API rate-limiting compliance. Output: enriched records + validation report.",

    # Original: "Implement a feature"
    "Implement dark mode toggle for our web application (React). Scope: persist preference in localStorage, smooth CSS transitions, all components must support both themes. Requirements: maintain accessibility (WCAG 2.1 AA), performance (<50ms toggle time). Test coverage: >90% for theme logic.",

    # Original: "Set up infrastructure"
    "Set up a CI/CD pipeline (GitHub Actions) for our Go microservice. Stages: test, build Docker image, push to ECR, deploy to ECS. Requirements: <10min pipeline duration, automatic rollback on failed health checks, deployment notifications to Slack. Output: pipeline YAML + runbook.",

    # Original: "Optimize performance"
    "Optimize database query performance for our user dashboard. Current: 5s load time (unacceptable). Constraints: cannot change schema. Approach: analyze slow queries, add indexes, refactor N+1 problems. Target: <500ms. Deliverable: before/after performance metrics + optimization summary.",

    # Original: "Reduce costs"
    "Reduce cloud infrastructure costs by 30% while maintaining performance SLAs. Current: $50k/month AWS spend. Provide: (1) cost analysis by service, (2) optimization opportunities ranked by impact, (3) implementation plan with risk assessment. Timeline: 6 weeks.",

    # Original: "Improve efficiency"
    "Improve deployment efficiency for our 20-service monorepo. Current: 45min manual build. Requirements: parallel builds, smart caching, automated testing before deploy. Target: <10min. Deliverable: build system design + migration plan + time savings analysis.",

    # Original: "Scale the system"
    "Scale our PostgreSQL database from 100k to 10M users. Strategy options: (1) read replicas, (2) sharding, (3) caching layer. Constraints: zero downtime required. Provide: analysis of each approach, recommendation with rationale, migration procedure, rollback plan.",

    # Original: "Enhance security"
    "Enhance application security with input validation and rate limiting. Scope: all public APIs. Requirements: prevent SQL injection, XSS, brute-force attacks. Standards: OWASP Top 10 compliance. Deliverable: implementation guide + before/after security audit + test cases.",

    # Original: "Analyze this dataset"
    "Analyze our e-commerce transaction dataset (1M records, 2 years). Goals: identify fraud patterns, seasonal trends, high-value customer segments. Methods: statistical analysis, clustering, anomaly detection. Output: Jupyter notebook with visualizations + actionable insights + fraud detection model.",

    # Original: "Review the code"
    "Review the attached pull request for our authentication module. Focus: security vulnerabilities, code quality, test coverage, performance. Provide: (1) detailed feedback per file, (2) risk assessment, (3) approval recommendation. Expected turnaround: 24 hours.",

    # Original: "Evaluate the design"
    "Evaluate our proposed database schema redesign. Criteria: scalability, query performance, maintainability, migration feasibility. Context: supporting 50M users. Deliverable: detailed assessment + risk analysis + recommendation (approve/reject/modify).",

    # Original: "Assess the proposal"
    "Assess the feasibility of migrating from monolith to microservices. Timeline: 12 months. Budget: $500k. Constraints: maintain feature parity, minimize downtime. Provide: (1) risk assessment, (2) cost-benefit analysis, (3) phased migration plan, (4) success metrics.",

    # Original: "Compare the options"
    "Compare 3 options for our caching strategy: Redis cluster, Memcached, or DynamoDB. Requirements: 100k req/sec, 99.9% uptime, <10ms latency. Evaluation: cost, operational complexity, latency, failure handling. Recommendation: detailed comparison matrix + rationale.",

    # Original: "Do something with the data"
    "Process our raw sensor telemetry data (10k sensors, 100B events/day) into meaningful insights. Transformations: aggregate by location, detect anomalies, forecast trends. Requirements: latency <5min, handle out-of-order events. Output: structured data for analytics + anomaly alerts.",

    # Original: "Handle user interactions"
    "Handle user authentication and authorization across our web and mobile apps. Requirements: JWT tokens, role-based access control (3 roles), session management, logout on all devices. Constraints: <200ms auth latency. Deliverable: auth service + client SDKs + integration guide.",

    # Original: "Process and store information"
    "Process incoming webhook events (100k/day from payment provider) and store in our database. Requirements: deduplicate, validate, enrich with customer context, ensure exactly-once delivery. Constraints: <5s processing latency. Output: event processor + schema + deployment guide.",

    # Original: "Generate and display results"
    "Generate automated weekly reports showing sales performance by region and product. Requirements: pull data from 5 data sources, create visualizations (charts, tables), send via email. Format: HTML + PDF. Target audience: regional managers (non-technical). Delivery: every Monday 8 AM.",

    # Original: "Manage and update records"
    "Manage customer records with change history tracking. Operations: create, update, delete (soft). Requirements: audit trail for compliance, conflict resolution for concurrent updates, bulk import support. Output: REST API + database schema + migration script.",

    # Original: "Validate and transform input"
    "Validate and transform CSV import data (customer records) before loading to database. Validations: required fields, email format, phone number, date ranges. Transformations: normalize case, standardize phone format, geocode addresses. Output: cleaned CSV + error report.",

    # Original: "Compute and cache values"
    "Compute expensive analytics metrics (top products, customer segments, revenue trends) and cache for dashboard. Requirements: precompute daily at 2 AM, invalidate on data changes, serve <100ms. Cache strategy: Redis. Deliverable: computation script + cache invalidation logic.",

    # Original: "Query and filter data"
    "Query our customer database with complex filters: (1) by purchase history, (2) by geographic region, (3) by tenure, (4) by engagement level. Requirements: support all filter combinations, <500ms response, export to CSV. Output: API endpoint + query optimization plan.",

    # Original: "Export and archive content"
    "Export user-generated content (documents, images, metadata) to long-term storage (AWS Glacier). Requirements: compress before archive, maintain directory structure, generate inventory, support recovery. Schedule: monthly. Output: automated script + recovery procedures.",

    # Original: "Monitor and alert on changes"
    "Monitor application health metrics and send alerts. Metrics: error rate >5%, response time >2s, DB connection pool >80% utilized. Alerts: Slack notification + PagerDuty escalation if not acknowledged in 5min. Dashboard: Grafana. Output: monitoring setup + alert configuration.",

    # Original: "Improve the workflow"
    "Improve our content review workflow to reduce processing time from 3 days to <4 hours. Current state: manual queue management, no progress tracking. Requirements: automated routing based on content type, real-time dashboard, approval audit trail, integration with Slack. Deliverable: workflow process design + tool selection + implementation guide + ROI analysis.",

    # Original: "Enhance user experience"
    "Enhance user experience in our checkout flow. Current metrics: 30% cart abandonment rate, avg 5 steps. Target: <15% abandonment, reduce steps to 3. Focus: streamline payment form, add progress indicator, enable guest checkout. Expected output: wireframes + prototype + A/B test plan + conversion metrics.",

    # Original: "Optimize resource usage"
    "Optimize resource usage in our Kubernetes cluster. Current: 60% CPU utilization but high variance, leading to frequent pod evictions. Constraints: maintain <2s service latency (p99). Provide: resource requests/limits optimization, autoscaling strategy, resource quota recommendations. Deliverable: updated k8s manifests + monitoring dashboard.",

    # Original: "Implement best practices"
    "Implement API security best practices across our 15 microservices. Standards: OWASP API security, rate limiting, input validation, authentication/authorization. Current state: inconsistent implementation. Constraints: zero-downtime deployment. Output: security framework + shared utilities library + deployment playbook + compliance checklist.",

    # Original: "Update the documentation"
    "Update system architecture documentation (currently 6 months outdated). Scope: service diagrams, data flow, deployment procedures, disaster recovery plan. Format: Markdown + draw.io diagrams. Audience: new engineers + stakeholders. Requirements: include examples, explain design decisions, link to relevant code. Timeline: 2 weeks.",
]

def generate_comparison_data():
    """Generate dataset with both deficient and improved prompts"""
    dataset = []

    for i, (deficient, improved) in enumerate(zip(DEFICIENT_PROMPTS, IMPROVED_PROMPTS), 1):
        dataset.append({
            "sample_id": f"SAMPLE_{i:03d}",
            "original_deficient_prompt": deficient,
            "claude_improved_prompt": improved,
            "missing_dimensions": identify_missing_dimensions(deficient),
            "timestamp": datetime.now().isoformat()
        })

    return dataset

def identify_missing_dimensions(prompt):
    """Identify which dimensions are likely missing from a deficient prompt"""
    # Simple heuristic-based detection
    missing = []

    if len(prompt) < 50:
        missing.extend(["clarity", "specificity", "completeness"])
    if "format" not in prompt.lower() and "output" not in prompt.lower():
        missing.append("expected_output")
    if "constraint" not in prompt.lower() and "limit" not in prompt.lower():
        missing.append("constraints")
    if "require" not in prompt.lower() and "must" not in prompt.lower():
        missing.append("requirements")
    if "context" not in prompt.lower() and "background" not in prompt.lower():
        missing.append("context")
    if "reason" not in prompt.lower() and "why" not in prompt.lower():
        missing.append("actionability")

    # Ensure we identify at least 2 dimensions as missing
    if not missing:
        missing = ["clarity", "specificity"]

    return list(set(missing))[:8]  # Max 8 dimensions

if __name__ == "__main__":
    data = generate_comparison_data()

    # Save to JSON
    with open("dataset_50_samples.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Generated dataset with {len(data)} samples")
    print(f"✓ Saved to: dataset_50_samples.json")
