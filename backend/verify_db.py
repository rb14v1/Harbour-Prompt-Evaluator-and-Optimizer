#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evaluator.models import AgentOutput, EvaluationResult

print("\n=== SQLite DATABASE - Agent Outputs Check ===\n")

# Check latest evaluation
result = EvaluationResult.objects.latest('created_at')
print(f"Latest Evaluation ID: {result.id}")
print(f"Score: {result.final_score}/10")
print(f"\nAgent Outputs Saved for this evaluation:")
print(f"Total: {result.agent_outputs.count()} outputs\n")

if result.agent_outputs.count() > 0:
    print("✓ AGENT OUTPUTS ARE BEING SAVED!\n")
    for output in result.agent_outputs.all().order_by('iteration_number', 'executed_at'):
        print(f"  [{output.iteration_number}] {output.agent_name.upper():15} - Status: {output.status}")
        print(f"       Input keys:  {list(output.input_data.keys())[:3]}")
        print(f"       Output keys: {list(output.output_data.keys())[:3]}")
else:
    print("✗ No agent outputs found for latest evaluation\n")
    print("Note: Old evaluations won't have outputs (created before fix)")

print("\n")
