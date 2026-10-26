from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from enum import Enum


class DifficultyEnum(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class TestCaseSchema(BaseModel):
    prompt_id: str
    test_case_id: str
    input: str = Field(..., min_length=5, max_length=5000)
    expected_output: str = Field(..., min_length=5, max_length=10000)
    difficulty: DifficultyEnum
    category: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(default="", max_length=500)
    edge_case: bool = False

    @validator("input", "expected_output")
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v


class SyntheticDatasetSchema(BaseModel):
    dataset_size: int = Field(..., ge=1, le=100)
    test_cases: List[TestCaseSchema]

    @validator("test_cases")
    def validate_test_cases(cls, v, values):
        if "dataset_size" in values:
            dataset_size = values["dataset_size"]
            if len(v) < dataset_size * 0.7:
                raise ValueError(
                    f"Test cases count ({len(v)}) must be at least 70% of dataset_size ({dataset_size})"
                )
        return v

    def validate_difficulty_distribution(self) -> Dict[str, int]:
        distribution = {"Easy": 0, "Medium": 0, "Hard": 0}
        for tc in self.test_cases:
            distribution[tc.difficulty] += 1
        return distribution


class EvaluationDimensionSchema(BaseModel):
    name: str
    score: int = Field(..., ge=0, le=10)
    reasoning: str = Field(..., max_length=500)
    identified_issue: str = Field(..., max_length=500)
    recommendation: str = Field(..., max_length=500)


class EvaluationSchema(BaseModel):
    dimensions: Dict[str, EvaluationDimensionSchema]
    overall_score: float = Field(..., ge=0, le=10)
    summary: str = Field(..., max_length=1000)

    @validator("overall_score")
    def validate_overall_score(cls, v, values):
        if "dimensions" in values:
            dims = values["dimensions"]
            if dims:
                avg = sum(d.score for d in dims.values()) / len(dims)
                # Allow 0.5 tolerance for rounding
                if abs(v - avg) > 0.5:
                    raise ValueError(
                        f"Overall score {v} does not match average of dimensions {avg:.1f}"
                    )
        return v


class AnalysisSchema(BaseModel):
    prompt_intent: str = Field(..., max_length=500)
    user_objective: str = Field(..., max_length=500)
    explicit_requirements: List[str] = Field(..., max_items=10)
    implicit_requirements: List[str] = Field(..., max_items=10)
    context: str = Field(..., max_length=500)
    target_audience: str = Field(..., max_length=200)
    expected_output: str = Field(..., max_length=500)
    output_format: str = Field(..., max_length=200)
    constraints: List[str] = Field(..., max_items=10)
    dependencies: List[str] = Field(default=[], max_items=10)
    missing_information: List[str] = Field(default=[], max_items=10)
    ambiguities: List[str] = Field(default=[], max_items=10)
    potential_failure_modes: List[str] = Field(..., max_items=10)
    risks: List[str] = Field(..., max_items=10)
    edge_cases: List[str] = Field(..., max_items=10)
    complexity: str = Field(..., pattern="^(Low|Medium|High)$")
    important_assumptions: List[str] = Field(..., max_items=10)


class EvaluateRequestSchema(BaseModel):
    department: str = Field(..., min_length=1, max_length=100)
    task_type: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=5, max_length=10000)
    dataset_size: int = Field(default=5, ge=1, le=100)
    num_datasets: int = Field(default=50, ge=1, le=50)
    prompt_id: Optional[str] = Field(default=None, max_length=50)

    @validator("prompt")
    def strip_prompt(cls, v):
        return v.strip()


class ImprovementMetadataSchema(BaseModel):
    explanation_of_changes: List[str] = Field(..., max_items=10)
    structural_sections_added: List[str] = Field(..., max_items=10)


class ValidationReportSchema(BaseModel):
    is_valid: bool
    total_cases_validated: int
    target_dataset_size: int
    difficulty_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    edge_cases_count: int
    issues_detected_and_repaired: List[str] = Field(default=[], max_items=50)
    validation_status: str = Field(..., pattern="^(Passed|Repaired & Passed)$")


class ComparisonSchema(BaseModel):
    dimension_improvements: Dict[str, float]
    overall_difference: float = Field(..., ge=-10, le=10)
    improved_dimensions: List[str]
    unchanged_dimensions: List[str]
    regressed_dimensions: List[str]
    key_insights: List[str] = Field(default=[], max_items=5)


class PromptEvaluationResponseSchema(BaseModel):
    id: Optional[int] = None
    prompt_id: str
    department: str
    task_type: str
    original_prompt: str
    processed_prompt: str
    analysis: AnalysisSchema
    evaluation: EvaluationSchema
    synthetic_dataset: SyntheticDatasetSchema
    dataset_summary: Dict[str, Any] = {}
    improved_prompt: str
    improvement_metadata: ImprovementMetadataSchema
    re_evaluation: EvaluationSchema
    comparison: ComparisonSchema
    overall_original_score: float
    overall_improved_score: float
    score_difference: float
    status: str = Field(..., pattern="^(COMPLETED|PROCESSING|ERROR)$")
