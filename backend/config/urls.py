from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from evaluator.views import PromptEvaluationViewSet, PromptHistoryViewSet

router = DefaultRouter()
router.register(r'evaluations', PromptEvaluationViewSet, basename='evaluation')
router.register(r'history', PromptHistoryViewSet, basename='history')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/health/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
]
