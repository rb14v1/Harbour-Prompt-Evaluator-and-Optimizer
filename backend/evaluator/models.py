from django.db import models
from django.contrib.auth.models import User
import json
import uuid

class Prompt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompts', null=True, blank=True)
    original_prompt = models.TextField()
    processed_prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prompt {self.id}: {self.original_prompt[:50]}..."


class Classification(models.Model):
    TASK_CATEGORIES = [
        ('create_content', 'Create Content'),
        ('create_code', 'Create Code'),
        ('research', 'Research'),
        ('deep_research', 'Deep Research / Analysis'),
        ('plan_organize', 'Plan and Organize'),
        ('ideate', 'Ideate'),
        ('summarize', 'Summarize'),
        ('explain', 'Explain'),
        ('optimize', 'Optimize'),
    ]

    COMPLEXITY_LEVELS = [
        ('simple', 'Simple'),
        ('moderate', 'Moderate'),
        ('complex', 'Complex'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name='classification')
    task_type = models.CharField(max_length=50, choices=TASK_CATEGORIES)
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_LEVELS)
    confidence = models.FloatField(help_text="Confidence score 0.0-1.0")
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.get_complexity_display()}"


class Analysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name='analysis')
    intent = models.TextField()
    requirements = models.JSONField(default=list)
    context = models.JSONField(default=list)
    constraints = models.JSONField(default=list)
    expected_output = models.TextField()
    missing_information = models.JSONField(default=list)
    ambiguities = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.prompt.id}"


class DimensionScore(models.Model):
    QUALITY_LEVELS = [
        ('poor', 'Poor'),
        ('moderate', 'Moderate'),
        ('good', 'Good'),
        ('excellent', 'Excellent'),
    ]

    DIMENSIONS = [
        ('clarity', 'Clarity'),
        ('specificity', 'Specificity'),
        ('context', 'Context'),
        ('completeness', 'Completeness'),
        ('requirements', 'Requirements'),
        ('constraints', 'Constraints'),
        ('expected_output', 'Expected Output'),
        ('actionability', 'Actionability'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dimension = models.CharField(max_length=50, choices=DIMENSIONS)
    level = models.CharField(max_length=20, choices=QUALITY_LEVELS)
    score = models.FloatField(help_text="Numerical score: 2.5, 5.0, 7.5, or 10.0")
    issues = models.JSONField(default=list)
    evidence = models.TextField()
    recommendation = models.TextField()

    class Meta:
        unique_together = ('id', 'dimension')

    def __str__(self):
        return f"{self.get_dimension_display()}: {self.get_level_display()}"


class Evaluation(models.Model):
    STATUS_CHOICES = [
        ('needs_improvement', 'Needs Improvement'),
        ('ready', 'Ready'),
        ('in_progress', 'In Progress'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name='evaluation')
    dimension_scores = models.ManyToManyField(DimensionScore)
    overall_score = models.FloatField()
    threshold = models.FloatField(default=7.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    low_scoring_dimensions = models.JSONField(default=list)
    high_performing_dimensions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evaluation {self.id}: Score {self.overall_score}"


class PromptImprovement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='improvements')
    improved_prompt = models.TextField()
    iteration_number = models.IntegerField()
    changes_made = models.JSONField(default=list)
    dimensions_addressed = models.JSONField(default=list)
    intent_preserved = models.BooleanField(default=True)
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['iteration_number']
        unique_together = ('original_prompt', 'iteration_number')

    def __str__(self):
        return f"Improvement {self.iteration_number} for {self.original_prompt.id}"


class EvaluationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name='result')
    original_prompt = models.TextField()
    final_prompt = models.TextField()
    initial_score = models.FloatField()
    final_score = models.FloatField()
    improvements_made = models.IntegerField(default=0)
    iterations_required = models.IntegerField(default=0)
    summary = models.TextField()
    status = models.CharField(max_length=20, choices=[('ready', 'Ready'), ('needs_manual_review', 'Needs Manual Review')])
    full_report = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result {self.id}: {self.final_score}"
