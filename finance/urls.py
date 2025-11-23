from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FinanceReportViewSet, StudentPaymentViewSet, TeacherPaymentViewSet,
    StaffPaymentViewSet, WalletViewSet, PaymentDiscountViewSet, IncomeLeadViewSet
)

router = DefaultRouter()
router.register(r'reports', FinanceReportViewSet, basename='finance-report')
router.register(r'student-payments', StudentPaymentViewSet, basename='student-payment')
router.register(r'teacher-payments', TeacherPaymentViewSet, basename='teacher-payment')
router.register(r'staff-payments', StaffPaymentViewSet, basename='staff-payment')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'discounts', PaymentDiscountViewSet, basename='discount')
router.register(r'leads', IncomeLeadViewSet, basename='lead')

urlpatterns = [
    path('', include(router.urls)),
]
