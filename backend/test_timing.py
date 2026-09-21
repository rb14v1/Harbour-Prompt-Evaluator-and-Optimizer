import os
import sys
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from evaluator.orchestrator import PromptEvaluationOrchestrator

print("\n=== TIMING TEST ===")
print("Prompt: 'Write hello world in Python'\n")

start = time.time()
orchestrator = PromptEvaluationOrchestrator()
result = orchestrator.evaluate('Write hello world in Python')
elapsed = time.time() - start

print(f"\nTotal Time: {elapsed:.1f}s ({elapsed/60:.2f}m)")
print(f"Initial Score: {result['initial_evaluation']['overall_score']:.2f}/10")
print(f"Final Score: {result['final_evaluation']['overall_score']:.2f}/10")
print(f"Iterations: {result['iterations_required']}/3")
print(f"Improvements: {result['improvements_made']}")
