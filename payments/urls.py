from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentMethodViewSet, TransactionViewSet, PaymentInitiateViewSet

router = DefaultRouter()
router.register(r'methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'initiate', PaymentInitiateViewSet, basename='payment-initiate')

urlpatterns = [
    path('', include(router.urls)),
]
