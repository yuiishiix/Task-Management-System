from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet
from . import views

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
urlpatterns = [
    path('api/v1/register/', views.register, name='register'),
    path('api/v1/login/', views.login, name='login'),
    path('api/v1/', include(router.urls)),  # You could make this '/api/v1/tasks/' for clarity
]

