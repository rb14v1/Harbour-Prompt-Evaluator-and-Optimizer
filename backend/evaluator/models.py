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
        ('research', 'Research'),
        ('deep_research', 'Deep Research / Analysis'),
        ('plan_organize', 'Plan and Organize'),
        ('ideate_brainstorm', 'Ideate / Brainstorm'),
        ('summarize_review', 'Summarize / Review'),
        ('explain_teach', 'Explain / Teach'),
        ('optimize_improve', 'Optimize / Improve'),
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
    ROLE_CHOICES = [
        ('software', 'Software'),
        ('communication', 'Communication'),
        ('design', 'Design'),
        ('engineering', 'Engineering'),
        ('finance', 'Finance'),
        ('human_resources', 'Human Resources'),
        ('learning_development', 'Learning and Development'),
        ('marketing', 'Marketing'),
        ('product_management', 'Product Management'),
        ('support', 'Support'),
        ('commercial', 'Commercial'),
        ('delivery_management', 'Delivery Management'),
        ('business_analysis', 'Business Analysis'),
    ]

    TASK_CHOICES = [
        ('create_content', 'Create Content'),
        ('research', 'Research'),
        ('deep_research', 'Deep Research / Analysis'),
        ('plan_organize', 'Plan and Organize'),
        ('ideate_brainstorm', 'Ideate / Brainstorm'),
        ('summarize_review', 'Summarize / Review'),
        ('explain_teach', 'Explain / Teach'),
        ('optimize_improve', 'Optimize / Improve'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name='result')
    original_prompt = models.TextField()
    final_prompt = models.TextField()
    user_role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)
    task_type = models.CharField(max_length=50, choices=TASK_CHOICES, blank=True, null=True)
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


class AgentOutput(models.Model):
    AGENT_CHOICES = [
        ('preprocessor', 'Preprocessor'),
        ('classifier', 'Classifier'),
        ('analyzer', 'Analyzer'),
        ('validator', 'Validator'),
        ('scoring', 'Scoring'),
        ('improver', 'Improver'),
        ('report', 'Report'),
    ]

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('skipped', 'Skipped'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation_result = models.ForeignKey(EvaluationResult, on_delete=models.CASCADE, related_name='agent_outputs')
    agent_name = models.CharField(max_length=50, choices=AGENT_CHOICES)
    iteration_number = models.IntegerField(default=0)
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    error_message = models.TextField(blank=True, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['iteration_number', 'executed_at']
        indexes = [
            models.Index(fields=['evaluation_result', 'agent_name']),
        ]

    def __str__(self):
        return f"{self.agent_name} - Iteration {self.iteration_number}"
