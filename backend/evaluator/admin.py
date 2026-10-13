from django.contrib import admin
from evaluator.models import (
    Prompt, Classification, Analysis, DimensionScore, Evaluation,
    PromptImprovement, EvaluationResult
)

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'original_prompt', 'created_at']
    search_fields = ['original_prompt', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'task_type', 'complexity', 'confidence']
    search_fields = ['prompt__original_prompt']
    readonly_fields = ['id', 'created_at']
    list_filter = ['task_type', 'complexity', 'created_at']


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'intent']
    search_fields = ['prompt__original_prompt', 'intent']
    readonly_fields = ['id', 'created_at']
    list_filter = ['created_at']


@admin.register(DimensionScore)
class DimensionScoreAdmin(admin.ModelAdmin):
    list_display = ['dimension', 'level', 'score']
    readonly_fields = ['id']
    list_filter = ['dimension', 'level']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'overall_score', 'status', 'created_at']
    search_fields = ['prompt__original_prompt']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']


@admin.register(PromptImprovement)
class PromptImprovementAdmin(admin.ModelAdmin):
    list_display = ['original_prompt', 'iteration_number', 'intent_preserved', 'created_at']
    search_fields = ['original_prompt__original_prompt', 'improved_prompt']
    readonly_fields = ['id', 'created_at']
    list_filter = ['iteration_number', 'intent_preserved', 'created_at']


@admin.register(EvaluationResult)
class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'initial_score', 'final_score', 'status', 'created_at']
    search_fields = ['prompt__original_prompt', 'summary']
    readonly_fields = ['id', 'full_report', 'created_at']
    list_filter = ['status', 'created_at']
