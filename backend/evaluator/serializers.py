from rest_framework import serializers
from evaluator.models import Prompt, Classification, Analysis, Evaluation, PromptImprovement, EvaluationResult

class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['id', 'user', 'original_prompt', 'processed_prompt', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ['id', 'prompt', 'task_type', 'complexity', 'confidence', 'reasoning', 'created_at']
        read_only_fields = ['id', 'created_at']


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = [
            'id', 'prompt', 'intent', 'requirements', 'context', 'constraints',
            'expected_output', 'missing_information', 'ambiguities', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = [
            'id', 'prompt', 'overall_score', 'threshold', 'status',
            'low_scoring_dimensions', 'high_performing_dimensions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PromptImprovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptImprovement
        fields = [
            'id', 'original_prompt', 'improved_prompt', 'iteration_number',
            'changes_made', 'dimensions_addressed', 'intent_preserved', 'reasoning', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EvaluationResultSerializer(serializers.ModelSerializer):
    initial_evaluation = serializers.SerializerMethodField()
    final_evaluation = serializers.SerializerMethodField()

    class Meta:
        model = EvaluationResult
        fields = [
            'id', 'prompt', 'original_prompt', 'final_prompt', 'initial_score',
            'final_score', 'improvements_made', 'iterations_required', 'summary',
            'status', 'full_report', 'initial_evaluation', 'final_evaluation', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_initial_evaluation(self, obj):
        """Extract initial_evaluation from full_report."""
        if obj.full_report:
            return obj.full_report.get('initial_evaluation', {})
        return {}

    def get_final_evaluation(self, obj):
        """Extract final_evaluation from full_report."""
        if obj.full_report:
            return obj.full_report.get('final_evaluation', {})
        return {}


class PromptEvaluationRequestSerializer(serializers.Serializer):
    """Serializer for evaluation request."""
    prompt = serializers.CharField(required=True, help_text="The prompt to evaluate")

    def validate_prompt(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Prompt cannot be empty")
        return value


class PromptEvaluationResponseSerializer(serializers.Serializer):
    """Serializer for evaluation response."""
    id = serializers.CharField(required=False)
    prompt_id = serializers.CharField()
    original_prompt = serializers.CharField()
    initial_score = serializers.FloatField(required=False)
    final_score = serializers.FloatField(required=False)
    classification = serializers.JSONField()
    analysis = serializers.JSONField()
    initial_evaluation = serializers.JSONField()
    improvement_history = serializers.ListField()
    final_evaluation = serializers.JSONField()
    final_prompt = serializers.CharField()
    summary = serializers.CharField()
    status = serializers.CharField()
    improvements_made = serializers.IntegerField()
    iterations_required = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    execution_history = serializers.JSONField(required=False)
