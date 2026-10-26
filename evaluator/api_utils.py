from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    page_size_query_limit = 100
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class EvaluationFilter(SearchFilter):
    """Custom filter for evaluation searches."""
    search_fields = ['prompt_id', 'department', 'task_type', 'original_prompt']


class EvaluationOrdering(OrderingFilter):
    """Custom ordering for evaluations."""
    ordering_fields = ['created_at', 'overall_original_score', 'score_difference']
    ordering = ['-created_at']
