from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoyaltyBranchViewSet, LoyaltyPointViewSet

router = DefaultRouter()
router.register(r'branches', LoyaltyBranchViewSet, basename='loyalty-branch')
router.register(r'points', LoyaltyPointViewSet, basename='loyalty-point')

urlpatterns = [
    path('', include(router.urls)),
]
