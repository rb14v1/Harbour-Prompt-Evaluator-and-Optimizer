#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evaluator.models import AgentOutput, EvaluationResult

print("\n=== DATABASE CHECK ===\n")

# Check AgentOutput table
outputs = AgentOutput.objects.all()
print(f"Total Agent Outputs in DB: {outputs.count()}")

if outputs.count() > 0:
    print("\nRecent agent outputs:")
    for output in outputs[:10]:
        print(f"  - {output.agent_name} (iteration {output.iteration_number}): {output.status}")
else:
    print("  (No agent outputs saved yet)")

# Check EvaluationResult
results = EvaluationResult.objects.all()
print(f"\nTotal Evaluation Results: {results.count()}")
if results.count() > 0:
    latest = results.last()
    print(f"Latest result ID: {latest.id}")
    print(f"Score: {latest.final_score}/10")
    print(f"Agent outputs for this result: {latest.agent_outputs.count()}")

print("\n")
