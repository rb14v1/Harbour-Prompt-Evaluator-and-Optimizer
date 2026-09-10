from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, models

from evaluator.models import EvaluationResult, Prompt
from evaluator.serializers import (
    EvaluationResultSerializer,
    PromptSerializer,
    PromptEvaluationRequestSerializer,
    PromptEvaluationResponseSerializer
)
from evaluator.orchestrator import PromptEvaluationOrchestrator


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

                response_serializer = PromptEvaluationResponseSerializer(report)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
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
