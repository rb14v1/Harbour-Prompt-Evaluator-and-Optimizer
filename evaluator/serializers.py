from rest_framework import serializers
from .models import PromptEvaluation, SyntheticDataset, SyntheticTestCase

class EvaluationRequestSerializer(serializers.Serializer):
    department = serializers.CharField(required=True, allow_blank=False, max_length=100)
    task_type = serializers.CharField(required=True, allow_blank=False, max_length=100)
    prompt = serializers.CharField(required=True, allow_blank=False)
    dataset_size = serializers.IntegerField(required=False, default=5, min_value=1, max_value=100)
    prompt_id = serializers.CharField(required=False, allow_blank=True, max_length=50)


class SyntheticTestCaseSerializer(serializers.ModelSerializer):
    input = serializers.CharField(source="input_text")

    class Meta:
        model = SyntheticTestCase
        fields = [
            "test_case_id",
            "input",
            "expected_output",
            "difficulty",
            "category",
            "edge_case",
            "notes",
            "llm_score",
            "llm_verdict",
            "llm_reason"
        ]


class SyntheticDatasetSerializer(serializers.ModelSerializer):
    test_cases = SyntheticTestCaseSerializer(many=True, read_only=True)

    class Meta:
        model = SyntheticDataset
        fields = [
            "dataset_size",
            "summary_json",
            "validation_report_json",
            "test_cases",
            "created_at"
        ]


class PromptEvaluationSerializer(serializers.ModelSerializer):
    synthetic_dataset = serializers.SerializerMethodField()

    class Meta:
        model = PromptEvaluation
        fields = [
            "id",
            "prompt_id",
            "department",
            "task_type",
            "original_prompt",
            "processed_prompt",
            "analysis_json",
            "evaluation_json",
            "improved_prompt",
            "improvement_metadata_json",
            "test_case_validation_json",
            "re_evaluation_json",
            "comparison_json",
            "overall_original_score",
            "overall_improved_score",
            "score_difference",
            "synthetic_dataset",
            "created_at"
        ]

    def get_synthetic_dataset(self, obj):
        ds = obj.synthetic_dataset
        if ds:
            cases = ds.test_cases.all()
            return {
                "dataset_size": ds.dataset_size,
                "summary": ds.summary_json,
                "validation_summary": ds.validation_report_json,
                "test_cases": SyntheticTestCaseSerializer(cases, many=True).data
            }
        return None
