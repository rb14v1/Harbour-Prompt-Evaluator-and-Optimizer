from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, models
from django.http import FileResponse
import logging
import traceback
import json
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from evaluator.models import EvaluationResult, Prompt
from evaluator.serializers import (
    EvaluationResultSerializer,
    PromptSerializer,
    PromptEvaluationRequestSerializer,
    PromptEvaluationResponseSerializer
)
from evaluator.orchestrator import PromptEvaluationOrchestrator

logger = logging.getLogger(__name__)


class PromptEvaluationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for evaluating prompts.
    """
    queryset = EvaluationResult.objects.all()
    serializer_class = EvaluationResultSerializer
    permission_classes = []  # Allow unauthenticated access for testing

    def get_queryset(self):
        """Filter results by current user if authenticated."""
        if self.request.user and self.request.user.is_authenticated:
            return EvaluationResult.objects.filter(prompt__user=self.request.user)
        return EvaluationResult.objects.all()  # Return all for testing

    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        """
        Evaluate a new prompt.

        Request body:
        {
            "prompt": "Your prompt text here"
        }
        """
        serializer = PromptEvaluationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        prompt_text = serializer.validated_data['prompt']

        try:
            with transaction.atomic():
                # Create or get prompt (allow anonymous for testing)
                user = request.user if request.user.is_authenticated else None
                prompt_obj = Prompt.objects.create(
                    user=user,
                    original_prompt=prompt_text,
                    processed_prompt=prompt_text
                )

                # Run evaluation
                orchestrator = PromptEvaluationOrchestrator()
                report = orchestrator.evaluate(prompt_text)

                # Store result
                result = EvaluationResult.objects.create(
                    prompt=prompt_obj,
                    original_prompt=report['original_prompt'],
                    final_prompt=report['final_prompt'],
                    initial_score=report['initial_evaluation']['overall_score'],
                    final_score=report['final_evaluation']['overall_score'],
                    improvements_made=report['improvements_made'],
                    iterations_required=report['iterations_required'],
                    summary=report['summary'],
                    status=report['status'],
                    full_report=report
                )

                # Add result ID to report for response
                report['id'] = result.id

                response_serializer = PromptEvaluationResponseSerializer(report)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            error_msg = f"Evaluation failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            print(f"\n❌ ERROR: {error_msg}\n")
            return Response(
                {"error": str(e), "detail": "See backend logs for details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def batch_evaluate(self, request):
        """
        Batch evaluate multiple prompts.

        Request body:
        {
            "prompts": ["prompt1", "prompt2", "prompt3"]
        }
        """
        prompts = request.data.get('prompts', [])

        if not isinstance(prompts, list) or len(prompts) == 0:
            return Response(
                {"error": "Please provide a list of prompts"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            orchestrator = PromptEvaluationOrchestrator()
            results = []

            for prompt_text in prompts:
                try:
                    report = orchestrator.evaluate(prompt_text)
                    results.append(report)
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "prompt": prompt_text
                    })

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get detailed report for a specific evaluation."""
        try:
            result = self.get_object()
            serializer = self.get_serializer(result)
            return Response(serializer.data)
        except EvaluationResult.DoesNotExist:
            return Response(
                {"error": "Evaluation not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def export_excel(self, request, pk=None):
        """Export evaluation results to single comprehensive Excel sheet."""
        try:
            result = self.get_object()
            report = result.full_report

            wb = Workbook()
            ws = wb.active
            ws.title = "Evaluation Report"

            # Set column widths
            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 50
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 40

            # Define styles
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, size=12, color="FFFFFF")
            section_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            section_font = Font(bold=True, size=11)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            row = 1

            # ===== TITLE =====
            ws[f'A{row}'] = "PROMPT EVALUATION REPORT"
            ws[f'A{row}'].font = Font(bold=True, size=14)
            ws.merge_cells(f'A{row}:D{row}')
            row += 2

            # ===== SCORE SUMMARY =====
            ws[f'A{row}'] = "EVALUATION SUMMARY"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1

            initial_score = report.get('initial_evaluation', {}).get('overall_score', 'N/A')
            final_score = report.get('final_evaluation', {}).get('overall_score', 'N/A')

            ws[f'A{row}'] = "Initial Score"
            ws[f'B{row}'] = initial_score
            ws[f'C{row}'] = "Final Score"
            ws[f'D{row}'] = final_score
            row += 1

            ws[f'A{row}'] = "Status"
            ws[f'B{row}'] = report.get('status', 'N/A')
            ws[f'C{row}'] = "Threshold"
            ws[f'D{row}'] = 7.0
            row += 1

            ws[f'A{row}'] = "Iterations Required"
            ws[f'B{row}'] = report.get('iterations_required', 0)
            ws[f'C{row}'] = "Improvements Made"
            ws[f'D{row}'] = report.get('improvements_made', 0)
            row += 2

            # ===== PROMPTS =====
            ws[f'A{row}'] = "ORIGINAL PROMPT"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1

            original_prompt = report.get('original_prompt', '')
            ws[f'A{row}'] = original_prompt
            ws[f'A{row}'].alignment = Alignment(wrap_text=True, vertical='top')
            ws.merge_cells(f'A{row}:D{row}')
            ws.row_dimensions[row].height = 60
            row += 2

            if report.get('final_prompt') != report.get('original_prompt'):
                ws[f'A{row}'] = "IMPROVED PROMPT"
                ws[f'A{row}'].font = section_font
                ws[f'A{row}'].fill = section_fill
                ws.merge_cells(f'A{row}:D{row}')
                row += 1

                final_prompt = report.get('final_prompt', '')
                ws[f'A{row}'] = final_prompt
                ws[f'A{row}'].alignment = Alignment(wrap_text=True, vertical='top')
                ws.merge_cells(f'A{row}:D{row}')
                ws.row_dimensions[row].height = 60
                row += 2

            # ===== CLASSIFICATION & ANALYSIS =====
            ws[f'A{row}'] = "CLASSIFICATION & ANALYSIS"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1

            classification = report.get('classification', {})
            analysis = report.get('analysis', {})

            ws[f'A{row}'] = "Task Type"
            ws[f'B{row}'] = classification.get('task_type', 'N/A')
            ws[f'C{row}'] = "Complexity"
            ws[f'D{row}'] = classification.get('complexity', 'N/A')
            row += 1

            ws[f'A{row}'] = "Intent"
            ws[f'B{row}'] = analysis.get('intent', 'N/A')
            ws.merge_cells(f'B{row}:D{row}')
            row += 1

            ws[f'A{row}'] = "Missing Information"
            missing_info = ', '.join(analysis.get('missing_information', []))
            ws[f'B{row}'] = missing_info
            ws.merge_cells(f'B{row}:D{row}')
            ws[f'B{row}'].alignment = Alignment(wrap_text=True)
            ws.row_dimensions[row].height = 40
            row += 2

            # ===== VALIDATION DIMENSIONS =====
            ws[f'A{row}'] = "VALIDATION DIMENSIONS"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1

            # Header row for dimensions
            ws[f'A{row}'] = "Dimension"
            ws[f'B{row}'] = "Score"
            ws[f'C{row}'] = "Level"
            ws[f'D{row}'] = "Issues & Recommendations"
            for col in ['A', 'B', 'C', 'D']:
                ws[f'{col}{row}'].font = Font(bold=True)
                ws[f'{col}{row}'].fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
            row += 1

            validation = report.get('initial_evaluation', {}).get('validation', {})
            for dim_name, dim_data in validation.items():
                ws[f'A{row}'] = dim_name.replace('_', ' ').title()
                ws[f'B{row}'] = dim_data.get('score', 'N/A')
                ws[f'C{row}'] = dim_data.get('level', 'N/A')
                issues = dim_data.get('issues', [])
                rec = dim_data.get('recommendation', '')
                ws[f'D{row}'] = f"Issues: {', '.join(issues) if issues else 'None'}. Recommendation: {rec}"
                ws[f'D{row}'].alignment = Alignment(wrap_text=True)
                ws.row_dimensions[row].height = 30
                row += 1

            row += 1

            # ===== IMPROVEMENTS HISTORY =====
            improvements = report.get('improvement_history', [])
            if improvements:
                ws[f'A{row}'] = "IMPROVEMENT HISTORY"
                ws[f'A{row}'].font = section_font
                ws[f'A{row}'].fill = section_fill
                ws.merge_cells(f'A{row}:D{row}')
                row += 1

                for i, imp in enumerate(improvements, 1):
                    ws[f'A{row}'] = f"Iteration {i}"
                    ws[f'A{row}'].font = Font(bold=True, italic=True)
                    ws.merge_cells(f'A{row}:D{row}')
                    row += 1

                    ws[f'A{row}'] = "Improved Prompt"
                    ws[f'B{row}'] = imp.get('improved_prompt', '')
                    ws[f'B{row}'].alignment = Alignment(wrap_text=True)
                    ws.merge_cells(f'B{row}:D{row}')
                    ws.row_dimensions[row].height = 50
                    row += 1

                    ws[f'A{row}'] = "Changes Made"
                    changes = ', '.join(imp.get('changes_made', []))
                    ws[f'B{row}'] = changes
                    ws[f'B{row}'].alignment = Alignment(wrap_text=True)
                    ws.merge_cells(f'B{row}:D{row}')
                    ws.row_dimensions[row].height = 40
                    row += 1

                    ws[f'A{row}'] = "Dimensions Addressed"
                    dims = ', '.join(imp.get('dimensions_addressed', []))
                    ws[f'B{row}'] = dims
                    ws.merge_cells(f'B{row}:D{row}')
                    row += 1

                    ws[f'A{row}'] = "Intent Preserved"
                    ws[f'B{row}'] = "Yes" if imp.get('intent_preserved') else "No"
                    row += 2

            # ===== KEY GAPS & RECOMMENDATIONS =====
            ws[f'A{row}'] = "KEY GAPS & RECOMMENDATIONS"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1

            low_dims = report.get('final_evaluation', {}).get('low_scoring_dimensions', [])
            if low_dims:
                ws[f'A{row}'] = "Low Scoring Dimensions"
                ws[f'B{row}'] = ', '.join(low_dims)
                ws.merge_cells(f'B{row}:D{row}')
                row += 1

            ws[f'A{row}'] = "Summary"
            ws[f'B{row}'] = report.get('summary', '')
            ws[f'B{row}'].alignment = Alignment(wrap_text=True)
            ws.merge_cells(f'B{row}:D{row}')
            ws.row_dimensions[row].height = 50
            row += 1

            # Save to bytes
            excel_file = BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)

            # Return file
            filename = f"evaluation_{result.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            response = FileResponse(excel_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except EvaluationResult.DoesNotExist:
            return Response(
                {"error": "Evaluation not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            error_msg = f"Excel export failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return Response(
                {"error": "Export failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PromptHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing evaluation history.
    """
    queryset = EvaluationResult.objects.all()
    serializer_class = EvaluationResultSerializer
    permission_classes = []  # Allow unauthenticated access for testing

    def get_queryset(self):
        """Filter evaluations by current user if authenticated."""
        if self.request.user and self.request.user.is_authenticated:
            return EvaluationResult.objects.filter(prompt__user=self.request.user).order_by('-created_at')
        return EvaluationResult.objects.all().order_by('-created_at')  # Return all for testing

    @action(detail=True, methods=['get'])
    def evaluations(self, request, pk=None):
        """Get all evaluations for a specific prompt."""
        try:
            prompt = self.get_object()
            results = EvaluationResult.objects.filter(prompt=prompt)
            serializer = EvaluationResultSerializer(results, many=True)
            return Response(serializer.data)
        except Prompt.DoesNotExist:
            return Response(
                {"error": "Prompt not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for user's prompts."""
        if not request.user.is_authenticated:
            return Response({
                "total_prompts": 0,
                "total_evaluations": 0,
                "average_score": 0.0,
                "prompts_ready": 0,
                "prompts_needing_review": 0,
                "message": "Authentication required for user stats"
            })

        user_prompts = self.get_queryset()
        user_results = EvaluationResult.objects.filter(prompt__user=request.user)

        stats = {
            "total_prompts": user_prompts.count(),
            "total_evaluations": user_results.count(),
            "average_score": 0.0,
            "prompts_ready": 0,
            "prompts_needing_review": 0
        }

        if user_results.exists():
            avg_score = user_results.values_list('final_score', flat=True).aggregate(
                models.Avg('final_score')
            )
            stats['average_score'] = float(avg_score.get('final_score__avg', 0.0) or 0.0)
            stats['prompts_ready'] = user_results.filter(status='ready').count()
            stats['prompts_needing_review'] = user_results.filter(status='needs_manual_review').count()

        return Response(stats)
