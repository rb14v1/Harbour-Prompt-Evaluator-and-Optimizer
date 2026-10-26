from django.db import models

class PromptEvaluation(models.Model):
    prompt_id = models.CharField(max_length=50, unique=True, db_index=True)
    department = models.CharField(max_length=100)
    task_type = models.CharField(max_length=100)
    original_prompt = models.TextField()
    processed_prompt = models.TextField(blank=True, default="")

    # JSON artifacts
    analysis_json = models.JSONField(default=dict)
    evaluation_json = models.JSONField(default=dict)
    improved_prompt = models.TextField(blank=True, default="")
    improvement_metadata_json = models.JSONField(default=dict)
    re_evaluation_json = models.JSONField(default=dict)
    comparison_json = models.JSONField(default=dict)
    test_case_validation_json = models.JSONField(default=dict)

    # Aggregate scores
    overall_original_score = models.FloatField(default=0.0)
    overall_improved_score = models.FloatField(default=0.0)
    score_difference = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.prompt_id} - {self.department} ({self.task_type})"

    @property
    def synthetic_dataset(self):
        return self.datasets.filter(dataset_index=1).first()


class SyntheticDataset(models.Model):
    evaluation = models.ForeignKey(
        PromptEvaluation,
        on_delete=models.CASCADE,
        related_name="datasets"
    )
    dataset_index = models.PositiveIntegerField(default=1)
    dataset_size = models.IntegerField(default=5)
    summary_json = models.JSONField(default=dict)
    validation_report_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["dataset_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["evaluation", "dataset_index"],
                name="unique_dataset_index_per_evaluation"
            )
        ]

    def __str__(self):
        return f"Dataset {self.dataset_index} ({self.dataset_size} cases) for {self.evaluation.prompt_id}"


class SyntheticTestCase(models.Model):
    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    dataset = models.ForeignKey(
        SyntheticDataset,
        on_delete=models.CASCADE,
        related_name="test_cases"
    )
    test_case_id = models.CharField(max_length=50)
    input_text = models.TextField()
    expected_output = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="Medium")
    category = models.CharField(max_length=150, default="General")
    edge_case = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    llm_score = models.FloatField(null=True, blank=True)
    llm_verdict = models.CharField(max_length=10, blank=True, default="")
    llm_reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.test_case_id} ({self.difficulty}) - {self.category}"
