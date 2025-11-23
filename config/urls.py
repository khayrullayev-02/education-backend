from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# Spectacular
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Auth
from auth_system.views import (
    LoginView, RegisterView, UserProfileView, ChangePasswordView,
    OrganizationViewSet, UserViewSet
)

# Finance
from finance.views import (
    FinanceReportViewSet, StudentPaymentViewSet, TeacherPaymentViewSet,
    StaffPaymentViewSet, WalletViewSet, PaymentDiscountViewSet, IncomeLeadViewSet
)

# Admin Dashboard
from admin_dashboard.views import (
    StudentManagementViewSet, DocumentApprovalViewSet, AttendanceManagementViewSet,
    LessonMaterialViewSet, ExamAnswerViewSet, AttendanceCorrectionViewSet
)

# Teacher Dashboard
from teacher_dashboard.views import (
    TeacherDashboardViewSet, HomeworkViewSet, HomeworkSubmissionViewSet,
    TeacherPortfolioViewSet
)

# Manager & Director
from manager_dashboard.views import ManagerDashboardViewSet, PerformanceMetricsViewSet
from director_dashboard.views import DirectorDashboardViewSet

# Attendance & Exams
from attendance.views import AttendanceSubmissionViewSet, AttendanceViewSet
from exams.views import ExamViewSet, ExamResultViewSet, ExamUploadViewSet
from statistics_app.views import StatisticsViewSet

# Superadmin Dashboard
from superadmin_dashboard.views import (
    SuperadminOrganizationViewSet, SuperadminUserViewSet, SuperadminAuditLogViewSet,
    SubscriptionTypeViewSet
)

# Payments
from payments.views import (
    PaymentMethodViewSet, TransactionViewSet, PaymentInitiateViewSet
)

# Notifications
from notifications.views import (
    NotificationViewSet, EmailTemplateViewSet,
    NotificationLogViewSet, NotificationTemplateViewSet
)

# Router
router = DefaultRouter()

# Auth
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'users', UserViewSet, basename='user')

# Finance
router.register(r'finance/reports', FinanceReportViewSet, basename='finance-report')
router.register(r'finance/student-payments', StudentPaymentViewSet, basename='student-payment')
router.register(r'finance/teacher-payments', TeacherPaymentViewSet, basename='teacher-payment')
router.register(r'finance/staff-payments', StaffPaymentViewSet, basename='staff-payment')
router.register(r'finance/wallets', WalletViewSet, basename='wallet')
router.register(r'finance/discounts', PaymentDiscountViewSet, basename='discount')
router.register(r'finance/leads', IncomeLeadViewSet, basename='lead')

# Admin Dashboard
router.register(r'admin/students', StudentManagementViewSet, basename='student')
router.register(r'admin/documents', DocumentApprovalViewSet, basename='document')
router.register(r'admin/attendance', AttendanceManagementViewSet, basename='admin-attendance')
router.register(r'admin/materials', LessonMaterialViewSet, basename='material')
router.register(r'admin/exam-answers', ExamAnswerViewSet, basename='exam-answer')
router.register(r'admin/corrections', AttendanceCorrectionViewSet, basename='correction')

# Teacher Dashboard
router.register(r'teacher/homework', HomeworkViewSet, basename='homework')
router.register(r'teacher/submissions', HomeworkSubmissionViewSet, basename='submission')
router.register(r'teacher/portfolio', TeacherPortfolioViewSet, basename='portfolio')

# Manager Dashboard
router.register(r'manager/metrics', PerformanceMetricsViewSet, basename='metric')

# Attendance
router.register(r'attendance/submit', AttendanceSubmissionViewSet, basename='attendance-submit')
router.register(r'attendance/records', AttendanceViewSet, basename='attendance-record')

# Exams
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'exams/results', ExamResultViewSet, basename='exam-result')
router.register(r'exams/uploads', ExamUploadViewSet, basename='exam-upload')

# Statistics
router.register(r'statistics', StatisticsViewSet, basename='statistics')

# Superadmin Dashboard
router.register(r'superadmin/organizations', SuperadminOrganizationViewSet, basename='superadmin-organization')
router.register(r'superadmin/users', SuperadminUserViewSet, basename='superadmin-user')
router.register(r'superadmin/audit-logs', SuperadminAuditLogViewSet, basename='audit-log')
router.register(r'superadmin/subscriptions', SubscriptionTypeViewSet, basename='subscription-type')

# Payments
router.register(r'payments/methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'payments/transactions', TransactionViewSet, basename='transaction')
router.register(r'payments/initiate', PaymentInitiateViewSet, basename='payment-initiate')

# Notifications
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notifications/templates', NotificationTemplateViewSet, basename='notification-template')
router.register(r'notifications/email-templates', EmailTemplateViewSet, basename='email-template')
router.register(r'notifications/logs', NotificationLogViewSet, basename='notification-log')


urlpatterns = [
    path('admin/', admin.site.urls),

    # API Router
    path('api/', include(router.urls)),

    # Auth
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Dashboards
    path('api/admin/dashboard/', include('admin_dashboard.urls')),
    path('api/director/dashboard/', DirectorDashboardViewSet.as_view({'get': 'list'}), name='director-dashboard'),
    path('api/manager/dashboard/', ManagerDashboardViewSet.as_view({'get': 'list'}), name='manager-dashboard'),
    path('api/teacher/dashboard/', TeacherDashboardViewSet.as_view({'get': 'list'}), name='teacher-dashboard'),
    path('api/superadmin/dashboard/', include('superadmin_dashboard.urls')),

    # Spectacular / Swagger / Redoc
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # DRF auth login
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
