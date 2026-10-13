#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evaluator.models import AgentOutput

old_count = AgentOutput.objects.count()
AgentOutput.objects.all().delete()
print(f"✅ Deleted {old_count} old agent output records")
print(f"✅ Fresh slate - AgentOutput table is now clean")
print(f"✅ Ready to store new agent outputs properly!")
