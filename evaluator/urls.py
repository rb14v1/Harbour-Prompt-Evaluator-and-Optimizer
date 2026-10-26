from django.urls import path
from .views import (
    EvaluatePromptView,
    EvaluatePromptStreamView,
    EvaluationListView,
    EvaluationDetailView,
    ExportExcelView,
    DirectExportExcelView
)

urlpatterns = [
    path("evaluate/", EvaluatePromptView.as_view(), name="evaluate-prompt"),
    path("evaluate/stream/", EvaluatePromptStreamView.as_view(), name="evaluate-prompt-stream"),
    path("evaluations/", EvaluationListView.as_view(), name="evaluation-list"),
    path("evaluations/<int:pk>/", EvaluationDetailView.as_view(), name="evaluation-detail"),
    path("evaluations/<int:pk>/export-excel/", ExportExcelView.as_view(), name="export-excel"),
    path("export-excel/", DirectExportExcelView.as_view(), name="direct-export-excel"),
]
