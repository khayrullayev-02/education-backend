from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, timedelta
from core.models import Group, Teacher, Student, Lesson, Attendance, Branch
from finance.models import FinanceReport
from .models import PerformanceMetrics, NotificationAlert
from .serializers import (
    GroupTransferSerializer, TeacherReassignmentSerializer,
    PerformanceMetricsSerializer, NotificationAlertSerializer
)
from auth_system.permissions import IsManager


class ManagerDashboardViewSet(viewsets.ViewSet):
    # permission_classes = [IsManager]
    permission_classes = [AllowAny]

    # Swagger va router xato bermasligi uchun qo‘shildi
    def list(self, request):
        return Response({
            "detail": "Manager Dashboard API is working.",
            "available_endpoints": [
                "overview",
                "attendance_overview",
                "transfer_student",
                "reassign_teacher",
                "teacher_performance",
                "student_progress",
                "financial_summary",
                "alerts"
            ]
        })

    @action(detail=False, methods=['get'])
    def overview(self, request):
        user = request.user
        branch = user.branch if user.branch else None

        if not branch:
            return Response({'error': 'Branch not found'}, status=status.HTTP_400_BAD_REQUEST)

        stats = {
            'total_teachers': Teacher.objects.filter(branch=branch).count(),
            'total_students': Student.objects.filter(branch=branch).count(),
            'active_groups': Group.objects.filter(branch=branch).count(),
            'pending_alerts': NotificationAlert.objects.filter(branch=branch, is_processed=False).count(),
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def attendance_overview(self, request):
        branch = request.user.branch
        today = datetime.today().date()

        lessons_today = Lesson.objects.filter(
            branch=branch,
            start_time__date=today
        )

        attendance_stats = {
            'total_lessons': lessons_today.count(),
            'scheduled': lessons_today.filter(is_cancelled=False).count(),
            'cancelled': lessons_today.filter(is_cancelled=True).count(),
            'student_attendance': Attendance.objects.filter(
                lesson__in=lessons_today
            ).values('status').annotate(count=Count('id'))
        }

        return Response(attendance_stats)

    @action(detail=False, methods=['post'])
    def transfer_student(self, request):
        serializer = GroupTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            student = Student.objects.get(id=serializer.validated_data['student_id'])
            from_group = Group.objects.get(id=serializer.validated_data['from_group_id'])
            to_group = Group.objects.get(id=serializer.validated_data['to_group_id'])

            from_group.students.remove(student)
            to_group.students.add(student)

            NotificationAlert.objects.create(
                branch=request.user.branch,
                alert_type='other',
                message=f"Student {student.user.get_full_name()} transferred from {from_group.name} to {to_group.name}"
            )

            return Response({'status': 'Student transferred successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reassign_teacher(self, request):
        serializer = TeacherReassignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            group = Group.objects.get(id=serializer.validated_data['group_id'])
            new_teacher = Teacher.objects.get(id=serializer.validated_data['new_teacher_id'])

            old_teacher_name = group.teacher.user.get_full_name() if group.teacher else "Unknown"
            group.teacher = new_teacher
            group.save()

            NotificationAlert.objects.create(
                branch=request.user.branch,
                alert_type='other',
                message=f"Teacher for group {group.name} changed from {old_teacher_name} to {new_teacher.user.get_full_name()}"
            )

            return Response({'status': 'Teacher reassigned successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def teacher_performance(self, request):
        branch = request.user.branch
        period_days = int(request.query_params.get('days', 30))
        start_date = datetime.today().date() - timedelta(days=period_days)

        teachers = Teacher.objects.filter(branch=branch)
        performance = []

        for teacher in teachers:
            late_count = Lesson.objects.filter(
                teacher=teacher,
                start_time__date__gte=start_date
            ).filter(
                attendance__status='late'
            ).count()

            total_lessons = Lesson.objects.filter(
                teacher=teacher,
                start_time__date__gte=start_date
            ).count()

            performance.append({
                'teacher_id': teacher.id,
                'name': teacher.user.get_full_name(),
                'late_count': late_count,
                'total_lessons': total_lessons,
                'punctuality_rate': ((total_lessons - late_count) / total_lessons * 100) if total_lessons > 0 else 100,
                'rating': teacher.performance_rating,
            })

        return Response(performance)

    @action(detail=False, methods=['get'])
    def student_progress(self, request):
        branch = request.user.branch
        students = Student.objects.filter(branch=branch)

        progress = []
        for student in students:
            total_attendance = Attendance.objects.filter(student=student).count()
            present = Attendance.objects.filter(student=student, status='present').count()

            groups = student.groups.all()

            progress.append({
                'student_id': student.id,
                'name': student.user.get_full_name(),
                'groups': [g.name for g in groups],
                'attendance_rate': (present / total_attendance * 100) if total_attendance > 0 else 0,
                'total_debt': float(student.total_debt),
                'status': student.status,
            })

        return Response(progress)

    @action(detail=False, methods=['get'])
    def financial_summary(self, request):
        branch = request.user.branch
        period_days = int(request.query_params.get('days', 30))
        start_date = datetime.today().date() - timedelta(days=period_days)

        reports = FinanceReport.objects.filter(
            branch=branch,
            report_date__gte=start_date
        ).aggregate(
            total_income=Sum('total_student_payments'),
            total_expenses=Sum('teacher_payments') + Sum('staff_payments'),
            profit=Sum('profit')
        )

        return Response(reports)

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        branch = request.user.branch
        unprocessed = request.query_params.get('unprocessed', 'true') == 'true'

        query = NotificationAlert.objects.filter(branch=branch)
        if unprocessed:
            query = query.filter(is_processed=False)

        serializer = NotificationAlertSerializer(query, many=True)
        return Response(serializer.data)


class PerformanceMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PerformanceMetricsSerializer
    # permission_classes = [IsManager]
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['metric_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return PerformanceMetrics.objects.all()
        if user.branch:
            return PerformanceMetrics.objects.filter(branch=user.branch)
        return PerformanceMetrics.objects.none()
