from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from evaluator.views import PromptEvaluationViewSet, PromptHistoryViewSet
from evaluator.config import QUALITY_THRESHOLD, QUALITY_DIMENSIONS

router = DefaultRouter()
router.register(r'evaluations', PromptEvaluationViewSet, basename='evaluation')
router.register(r'history', PromptHistoryViewSet, basename='history')

def config_view(request):
    """Return centralized configuration"""
    import json
    from django.http import JsonResponse
    return JsonResponse({
        'threshold': QUALITY_THRESHOLD,
        'dimensions': QUALITY_DIMENSIONS
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/health/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
    path('api/config/', config_view),
]
