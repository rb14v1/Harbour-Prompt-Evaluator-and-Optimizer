import uuid
import json
import logging
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError as PydanticValidationError

from .models import PromptEvaluation, SyntheticDataset, SyntheticTestCase
from .serializers import EvaluationRequestSerializer, PromptEvaluationSerializer
from .services.langgraph_workflow import execute_evaluation_workflow
from .services.pipeline_runner import run_evaluation_pipeline
from .services.excel_exporter import ExcelExporter
from .schemas import EvaluateRequestSchema
from .exceptions import PromptEvaluationException, format_error_response

logger = logging.getLogger(__name__)


class DuplicatePromptIdError(Exception):
    pass


def _persist_evaluation(workflow_result, department, task_type, prompt, prompt_id):
    try:
        with transaction.atomic():
            eval_record = PromptEvaluation.objects.create(
                prompt_id=prompt_id,
                department=department,
                task_type=task_type,
                original_prompt=workflow_result.get("original_prompt", prompt),
                processed_prompt=workflow_result.get("processed_prompt", prompt),
                analysis_json=workflow_result.get("analysis", {}),
                evaluation_json=workflow_result.get("evaluation", {}),
                improved_prompt=workflow_result.get("improved_prompt", ""),
                improvement_metadata_json=workflow_result.get("improvement_metadata", {}),
                re_evaluation_json=workflow_result.get("re_evaluation", {}),
                comparison_json=workflow_result.get("comparison", {}),
                test_case_validation_json=workflow_result.get("test_case_validation", {}),
                overall_original_score=workflow_result.get("overall_original_score", 0.0),
                overall_improved_score=workflow_result.get("overall_improved_score", 0.0),
                score_difference=workflow_result.get("score_difference", 0.0)
            )

            # Dataset 1 from the pipeline, then datasets 2..N from the batch generator
            all_datasets = workflow_result.get("all_datasets") or [{
                "dataset_index": 1,
                "dataset": workflow_result.get("synthetic_dataset", {}),
                "validation_summary": workflow_result.get("validation_summary", {}),
                "dataset_summary": workflow_result.get("dataset_summary", {})
            }]

            for item in all_datasets:
                cases = item["dataset"].get("test_cases", [])
                ds_record = SyntheticDataset.objects.create(
                    evaluation=eval_record,
                    dataset_index=item["dataset_index"],
                    dataset_size=len(cases),
                    summary_json=item["dataset_summary"],
                    validation_report_json=item["validation_summary"]
                )
                SyntheticTestCase.objects.bulk_create([
                    SyntheticTestCase(
                        dataset=ds_record,
                        test_case_id=tc.get("test_case_id", f"TC-{idx:03d}"),
                        input_text=tc.get("input", ""),
                        expected_output=tc.get("expected_output", ""),
                        difficulty=tc.get("difficulty", "Medium"),
                        category=tc.get("category", "General"),
                        edge_case=tc.get("edge_case", False),
                        notes=tc.get("notes", ""),
                        llm_score=tc.get("llm_score"),
                        llm_verdict=tc.get("llm_verdict", ""),
                        llm_reason=tc.get("llm_reason", "")
                    )
                    for idx, tc in enumerate(cases, start=1)
                ])

            test_cases = all_datasets[0]["dataset"].get("test_cases", [])
    except Exception as e:
        if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e).lower():
            logger.warning(f"Duplicate prompt_id: {prompt_id}")
            raise DuplicatePromptIdError(prompt_id) from e
        raise

    response_payload = {
        "id": eval_record.id,
        "prompt_id": prompt_id,
        "department": department,
        "task_type": task_type,
        "original_prompt": workflow_result.get("original_prompt", prompt),
        "processed_prompt": workflow_result.get("processed_prompt", prompt),
        "analysis": workflow_result.get("analysis", {}),
        "evaluation": workflow_result.get("evaluation", {}),
        "synthetic_dataset": {
            "dataset_size": len(test_cases),
            "test_cases": test_cases,
            "validation_summary": workflow_result.get("validation_summary", {})
        },
        "synthetic_datasets": [
            {
                "dataset_index": item["dataset_index"],
                "dataset_size": len(item["dataset"].get("test_cases", [])),
                "test_cases": item["dataset"].get("test_cases", []),
                "validation_summary": item["validation_summary"],
                "dataset_summary": item["dataset_summary"]
            }
            for item in all_datasets
        ],
        "dataset_summary": workflow_result.get("dataset_summary", {}),
        "improved_prompt": workflow_result.get("improved_prompt", ""),
        "improvement_metadata": workflow_result.get("improvement_metadata", {}),
        "test_case_validation": workflow_result.get("test_case_validation", {}),
        "re_evaluation": workflow_result.get("re_evaluation", {}),
        "comparison": workflow_result.get("comparison", {}),
        "overall_original_score": workflow_result.get("overall_original_score", 0.0),
        "overall_improved_score": workflow_result.get("overall_improved_score", 0.0),
        "score_difference": workflow_result.get("score_difference", 0.0),
        "status": "COMPLETED"
    }

    logger.info(f"Evaluation persisted: {prompt_id} (ID: {eval_record.id})")
    return response_payload


class EvaluatePromptView(APIView):
    """
    POST /api/evaluate/
    Evaluates prompt across 15 dimensions, generates prompt-specific synthetic dataset,
    validates dataset, optimizes prompt, and re-evaluates.
    """

    def post(self, request):
        try:
            # Validate request with Pydantic
            try:
                req_data = EvaluateRequestSchema(**request.data)
            except PydanticValidationError as e:
                errors = {e["loc"][0]: e["msg"] for e in e.errors()}
                logger.warning(f"Request validation failed: {errors}")
                return Response(
                    {"error": "Invalid request", "details": errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            department = req_data.department
            task_type = req_data.task_type
            prompt = req_data.prompt
            dataset_size = req_data.dataset_size
            num_datasets = req_data.num_datasets
            prompt_id = req_data.prompt_id or f"PROMPT-{uuid.uuid4().hex[:6].upper()}"

            logger.info(f"Starting evaluation: {prompt_id} | {department} | {task_type} | {num_datasets} datasets")

            workflow_result = execute_evaluation_workflow(
                department=department,
                task_type=task_type,
                prompt=prompt,
                dataset_size=dataset_size,
                prompt_id=prompt_id,
                num_datasets=num_datasets
            )

            logger.info(f"Workflow completed: {prompt_id}")

            try:
                response_payload = _persist_evaluation(workflow_result, department, task_type, prompt, prompt_id)
            except DuplicatePromptIdError:
                return Response(
                    {"error": "Prompt ID already exists", "prompt_id": prompt_id},
                    status=status.HTTP_409_CONFLICT
                )

            return Response(response_payload, status=status.HTTP_200_OK)

        except PromptEvaluationException as e:
            logger.warning(f"Evaluation error: {e.error_code} - {e.message}")
            return Response(format_error_response(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error during evaluation: {str(e)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred. Please check logs for details."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EvaluatePromptStreamView(APIView):
    """
    POST /api/evaluate/stream/
    Same request and saved result as /api/evaluate/. Responds with newline-delimited JSON:
    start/done events per agent as it runs, then one result event with the saved payload.
    """

    def post(self, request):
        try:
            req_data = EvaluateRequestSchema(**request.data)
        except PydanticValidationError as e:
            errors = {err["loc"][0]: err["msg"] for err in e.errors()}
            logger.warning(f"Request validation failed: {errors}")
            return Response(
                {"error": "Invalid request", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        prompt_id = req_data.prompt_id or f"PROMPT-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"Starting streamed evaluation: {prompt_id} | {req_data.department} | {req_data.task_type} | {req_data.num_datasets} datasets")

        def event_stream():
            try:
                for event in run_evaluation_pipeline(
                    department=req_data.department,
                    task_type=req_data.task_type,
                    prompt=req_data.prompt,
                    dataset_size=req_data.dataset_size,
                    prompt_id=prompt_id,
                    num_datasets=req_data.num_datasets
                ):
                    if event["event"] == "result":
                        payload = _persist_evaluation(
                            event["state"], req_data.department, req_data.task_type, req_data.prompt, prompt_id
                        )
                        event = {"event": "result", "data": payload}
                    yield json.dumps(event, default=str) + "\n"
            except DuplicatePromptIdError:
                yield json.dumps({"event": "error", "status": 409, "error": "Prompt ID already exists", "prompt_id": prompt_id}) + "\n"
            except PromptEvaluationException as e:
                logger.warning(f"Evaluation error: {e.error_code} - {e.message}")
                yield json.dumps({"event": "error", "status": 400, "error": e.message}) + "\n"
            except Exception as e:
                logger.error(f"Unexpected error during streamed evaluation: {str(e)}", exc_info=True)
                yield json.dumps({"event": "error", "status": 500, "error": "An unexpected error occurred. Please check logs for details."}) + "\n"

        response = StreamingHttpResponse(event_stream(), content_type="application/x-ndjson")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class EvaluationListView(APIView):
    """
    GET /api/evaluations/
    Lists recent prompt evaluations with summary scores.
    Supports pagination and filtering.
    """

    def get(self, request):
        from .api_utils import StandardResultsSetPagination, EvaluationFilter, EvaluationOrdering
        from django.db.models import Q

        try:
            # Base queryset
            queryset = PromptEvaluation.objects.all()

            # Apply filters
            search = request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(prompt_id__icontains=search) |
                    Q(department__icontains=search) |
                    Q(task_type__icontains=search)
                )

            # Apply ordering
            ordering = request.GET.get('ordering', '-created_at')
            if ordering in ['-created_at', 'created_at', '-overall_original_score', 'overall_original_score', '-score_difference', 'score_difference']:
                queryset = queryset.order_by(ordering)

            # Apply pagination
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = PromptEvaluationSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = PromptEvaluationSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error listing evaluations: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to list evaluations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EvaluationDetailView(APIView):
    """
    GET /api/evaluations/<id>/
    Retrieves full evaluation details including synthetic dataset.
    """

    def get(self, request, pk):
        eval_obj = get_object_or_404(PromptEvaluation, pk=pk)
        serializer = PromptEvaluationSerializer(eval_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportExcelView(APIView):
    """
    GET /api/evaluations/<id>/export-excel/
    Downloads the Excel workbook report for a saved evaluation.
    """

    def get(self, request, pk):
        eval_obj = get_object_or_404(PromptEvaluation, pk=pk)

        # Build state representation for exporter
        test_cases = []
        summary = {}
        val_summary = {}
        ds = eval_obj.synthetic_dataset
        if ds:
            summary = ds.summary_json
            val_summary = ds.validation_report_json
            for tc in ds.test_cases.all():
                test_cases.append({
                    "test_case_id": tc.test_case_id,
                    "input": tc.input_text,
                    "expected_output": tc.expected_output,
                    "difficulty": tc.difficulty,
                    "category": tc.category,
                    "edge_case": tc.edge_case,
                    "notes": tc.notes
                })

        workflow_data = {
            "prompt_id": eval_obj.prompt_id,
            "department": eval_obj.department,
            "task_type": eval_obj.task_type,
            "original_prompt": eval_obj.original_prompt,
            "processed_prompt": eval_obj.processed_prompt,
            "analysis": eval_obj.analysis_json,
            "evaluation": eval_obj.evaluation_json,
            "synthetic_dataset": {
                "dataset_size": len(test_cases),
                "test_cases": test_cases
            },
            "synthetic_datasets": [
                {
                    "dataset_index": d.dataset_index,
                    "dataset_size": d.dataset_size,
                    "test_cases": [
                        {
                            "test_case_id": tc.test_case_id,
                            "input": tc.input_text,
                            "expected_output": tc.expected_output,
                            "difficulty": tc.difficulty,
                            "category": tc.category,
                            "edge_case": tc.edge_case,
                            "notes": tc.notes,
                            "llm_score": tc.llm_score,
                            "llm_verdict": tc.llm_verdict,
                            "llm_reason": tc.llm_reason
                        }
                        for tc in d.test_cases.all()
                    ]
                }
                for d in eval_obj.datasets.order_by("dataset_index")
            ],
            "dataset_summary": summary,
            "validation_summary": val_summary,
            "test_case_validation": eval_obj.test_case_validation_json,
            "improved_prompt": eval_obj.improved_prompt,
            "improvement_metadata": eval_obj.improvement_metadata_json,
            "re_evaluation": eval_obj.re_evaluation_json,
            "comparison": eval_obj.comparison_json,
            "overall_original_score": eval_obj.overall_original_score,
            "overall_improved_score": eval_obj.overall_improved_score,
            "score_difference": eval_obj.score_difference,
            "status": "COMPLETED"
        }

        stream = ExcelExporter.generate_workbook(workflow_data)
        filename = f"Prompt_Evaluation_{eval_obj.prompt_id}.xlsx"

        response = HttpResponse(
            stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DirectExportExcelView(APIView):
    """
    POST /api/export-excel/
    Directly generates an Excel file from provided JSON payload.
    """

    def post(self, request):
        payload = request.data
        if not payload:
            return Response({"error": "Empty payload"}, status=status.HTTP_400_BAD_REQUEST)

        stream = ExcelExporter.generate_workbook(payload)
        pid = payload.get("prompt_id", "PROMPT-REPORT")
        filename = f"Prompt_Evaluation_{pid}.xlsx"

        response = HttpResponse(
            stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
