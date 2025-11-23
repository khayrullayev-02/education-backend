from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SuperadminAuditLogViewSet, OrganizationSettingsViewSet,
    SuperadminOrganizationViewSet, SuperadminUserViewSet, SubscriptionTypeViewSet
)

router = DefaultRouter()
router.register(r'audit-logs', SuperadminAuditLogViewSet, basename='audit-log')
router.register(r'org-settings', OrganizationSettingsViewSet, basename='org-settings')
router.register(r'organizations', SuperadminOrganizationViewSet, basename='organization')
router.register(r'users', SuperadminUserViewSet, basename='user')
router.register(r'subscription-types', SubscriptionTypeViewSet, basename='subscription-type')

urlpatterns = [
    path('', include(router.urls)),
]
