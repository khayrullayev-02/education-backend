from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import DocumentApproval, LessonMaterial, ExamAnswer, AttendanceCorrection
from .serializers import (
    DocumentApprovalSerializer, LessonMaterialSerializer, ExamAnswerSerializer,
    AttendanceCorrectionSerializer, StudentDetailSerializer
)
from core.models import Student, Attendance, Group, Lesson
from auth_system.permissions import IsAdmin

# Attendance uchun serializer
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class StudentManagementViewSet(viewsets.ModelViewSet):
    serializer_class = StudentDetailSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['enrollment_date', 'total_debt']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Student.objects.none()
        if getattr(user, 'role', None) == 'superadmin':
            return Student.objects.all()
        if getattr(user, 'branch', None):
            return Student.objects.filter(branch=user.branch)
        return Student.objects.none()

    @action(detail=False, methods=['get'])
    def debtors(self, request):
        students = self.get_queryset().filter(total_debt__gt=0).order_by('-total_debt')
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def block_student(self, request, pk=None):
        student = self.get_object()
        student.user.is_blocked = True
        student.user.save()
        return Response({'status': 'Student blocked'})

    @action(detail=True, methods=['post'])
    def unblock_student(self, request, pk=None):
        student = self.get_object()
        student.user.is_blocked = False
        student.user.save()
        return Response({'status': 'Student unblocked'})


class DocumentApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentApprovalSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['uploaded_at', 'status']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return DocumentApproval.objects.none()
        if getattr(user, 'role', None) == 'superadmin':
            return DocumentApproval.objects.all()
        if getattr(user, 'branch', None):
            return DocumentApproval.objects.filter(student__branch=user.branch)
        return DocumentApproval.objects.none()

    @action(detail=False, methods=['get'])
    def pending(self, request):
        docs = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(docs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        doc = self.get_object()
        doc.status = 'approved'
        doc.approved_by = request.user
        doc.approved_at = datetime.now()
        doc.save()
        return Response({'status': 'Document approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        doc = self.get_object()
        doc.status = 'rejected'
        doc.rejection_reason = request.data.get('reason', '')
        doc.save()
        return Response({'status': 'Document rejected'})


class AttendanceManagementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Attendance.objects.none()
        if getattr(user, 'role', None) == 'superadmin':
            return Attendance.objects.all()
        if getattr(user, 'branch', None):
            return Attendance.objects.filter(lesson__branch=user.branch)
        return Attendance.objects.none()

    @action(detail=False, methods=['get'])
    def daily_attendance(self, request):
        today = datetime.today().date()
        branch = request.query_params.get('branch')
        group = request.query_params.get('group')

        query = self.get_queryset().filter(lesson__start_time__date=today)
        if branch:
            query = query.filter(lesson__branch__id=branch)
        if group:
            query = query.filter(lesson__group__id=group)

        stats = {
            'total': query.count(),
            'present': query.filter(status='present').count(),
            'absent': query.filter(status='absent').count(),
            'late': query.filter(status='late').count(),
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def student_attendance(self, request):
        student_id = request.query_params.get('student')
        days = int(request.query_params.get('days', 30))

        if not student_id:
            return Response({'error': 'student parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        start_date = datetime.today().date() - timedelta(days=days)
        attendance = self.get_queryset().filter(
            student__id=student_id,
            lesson__start_time__date__gte=start_date
        ).values('status').annotate(count=Count('id'))

        return Response({
            'student_id': student_id,
            'period_days': days,
            'attendance_stats': attendance
        })

    @action(detail=False, methods=['get'])
    def teacher_lateness(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = datetime.today().date() - timedelta(days=days)

        late_teachers = Lesson.objects.filter(
            start_time__date__gte=start_date
        ).values('teacher__user__first_name', 'teacher__user__last_name').annotate(
            late_count=Count('id', filter=Q(attendance__status='late'))
        ).filter(late_count__gt=0).order_by('-late_count')

        return Response(late_teachers)


class LessonMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = LessonMaterialSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'lesson__group__name']
    ordering_fields = ['uploaded_at', 'file_type']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return LessonMaterial.objects.none()
        if getattr(user, 'role', None) == 'superadmin':
            return LessonMaterial.objects.all()
        if getattr(user, 'branch', None):
            return LessonMaterial.objects.filter(lesson__branch=user.branch)
        return LessonMaterial.objects.none()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ExamAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = ExamAnswerSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['exam__title', 'exam__group__name']
    ordering_fields = ['uploaded_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ExamAnswer.objects.none()
        if getattr(user, 'role', None) == 'superadmin':
            return ExamAnswer.objects.all()
        if getattr(user, 'branch', None):
            return ExamAnswer.objects.filter(exam__group__branch=user.branch)
        return ExamAnswer.objects.none()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class AttendanceCorrectionViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceCorrectionSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['corrected_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return AttendanceCorrection.objects.none()
        if getattr(user, 'role', None) == 'superadmin':
            return AttendanceCorrection.objects.all()
        if getattr(user, 'branch', None):
            return AttendanceCorrection.objects.filter(original_attendance__lesson__branch=user.branch)
        return AttendanceCorrection.objects.none()

    def perform_create(self, serializer):
        obj = serializer.save(corrected_by=self.request.user)
        attendance = obj.original_attendance
        attendance.status = obj.new_status
        attendance.save()
