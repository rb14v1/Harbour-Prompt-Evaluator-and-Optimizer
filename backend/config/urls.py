from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from evaluator.views import PromptEvaluationViewSet, PromptHistoryViewSet
from evaluator.config import QUALITY_THRESHOLD, QUALITY_DIMENSIONS, MAX_ITERATIONS

def config_view(request):
    """Return evaluator configuration"""
    return JsonResponse({
        'threshold': QUALITY_THRESHOLD,
        'max_iterations': MAX_ITERATIONS,
        'dimensions': QUALITY_DIMENSIONS
    })

router = DefaultRouter()
router.register(r'evaluations', PromptEvaluationViewSet, basename='evaluation')
router.register(r'history', PromptHistoryViewSet, basename='history')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/health/', lambda r: JsonResponse({'status': 'ok'})),
    path('api/config/', config_view),
]
