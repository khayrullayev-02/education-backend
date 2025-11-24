from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, CourseViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('', include(router.urls)),
]
