from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentManagementViewSet, DocumentApprovalViewSet, AttendanceManagementViewSet,
    LessonMaterialViewSet, ExamAnswerViewSet, AttendanceCorrectionViewSet
)

router = DefaultRouter()
router.register(r'students', StudentManagementViewSet, basename='student')
router.register(r'documents', DocumentApprovalViewSet, basename='document')
router.register(r'attendance', AttendanceManagementViewSet, basename='attendance')
router.register(r'materials', LessonMaterialViewSet, basename='material')
router.register(r'exam-answers', ExamAnswerViewSet, basename='exam-answer')
router.register(r'corrections', AttendanceCorrectionViewSet, basename='correction')

urlpatterns = [
    path('', include(router.urls)),
]
