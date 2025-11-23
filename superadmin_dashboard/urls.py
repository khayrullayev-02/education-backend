from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SuperadminAuditLogViewSet, OrganizationSettingsViewSet

router = DefaultRouter()
router.register(r'audit-logs', SuperadminAuditLogViewSet, basename='audit-log')
router.register(r'org-settings', OrganizationSettingsViewSet, basename='org-settings')

urlpatterns = [
    path('', include(router.urls)),
]
