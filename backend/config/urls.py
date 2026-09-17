from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from evaluator.views import PromptEvaluationViewSet, PromptHistoryViewSet

router = DefaultRouter()
router.register(r'evaluations', PromptEvaluationViewSet, basename='evaluation')
router.register(r'history', PromptHistoryViewSet, basename='history')

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'Backend is running'})

urlpatterns = [
    path('', health_check),
    path('api/', include(router.urls)),
    path('api/health/', health_check),
    path('admin/', admin.site.urls),
]
