from rest_framework import viewsets, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Avg, Q
from datetime import datetime
from core.models import Group, Attendance, Lesson, Student
from .models import Homework, HomeworkSubmission, TeacherPortfolio
from .serializers import (
    HomeworkSerializer, HomeworkSubmissionSerializer, TeacherPortfolioSerializer
)
from auth_system.permissions import IsTeacher
from finance.models import Wallet

# -----------------------
# Teacher Dashboard
# -----------------------
class TeacherDashboardViewSet(viewsets.GenericViewSet):  # GenericViewSet ishlatiladi
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    # Dummy list action DRF Spectacular uchun
    def list(self, request, *args, **kwargs):
        return Response({"detail": "Use specific actions like /overview or /my_groups"})

    @action(detail=False, methods=['get'])
    def overview(self, request):
        if request.user.role != 'teacher':
            return Response({'error': 'Only teachers can access this'}, status=status.HTTP_403_FORBIDDEN)

        try:
            teacher = request.user.teacher
            groups = Group.objects.filter(teacher=teacher)

            total_students = sum([group.students.count() for group in groups])

            stats = {
                'teacher_id': teacher.id,
                'name': request.user.get_full_name(),
                'groups': groups.count(),
                'total_students': total_students,
                'pending_homework': Homework.objects.filter(
                    teacher=teacher,
                    status='assigned'
                ).count(),
                'ungraded_submissions': HomeworkSubmission.objects.filter(
                    homework__teacher=teacher,
                    grade__isnull=True
                ).count(),
            }
            return Response(stats)
        except AttributeError:
            return Response({'error': 'Teacher profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def my_groups(self, request):
        if request.user.role != 'teacher':
            return Response({'error': 'Only teachers can access this'}, status=status.HTTP_403_FORBIDDEN)

        teacher = request.user.teacher
        groups = Group.objects.filter(teacher=teacher)

        group_data = []
        for group in groups:
            group_data.append({
                'id': group.id,
                'name': group.name,
                'subject': group.subject,
                'student_count': group.students.count(),
                'level': group.level,
            })

        return Response(group_data)

    @action(detail=False, methods=['get'])
    def student_attendance(self, request):
        if request.user.role != 'teacher':
            return Response({'error': 'Only teachers can access this'}, status=status.HTTP_403_FORBIDDEN)

        group_id = request.query_params.get('group')
        if not group_id:
            return Response({'error': 'group parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(id=group_id)
            students = group.students.all()

            attendance_data = []
            for student in students:
                attended = Attendance.objects.filter(
                    student=student,
                    lesson__group=group,
                    status='present'
                ).count()

                total = Attendance.objects.filter(
                    student=student,
                    lesson__group=group
                ).count()

                attendance_data.append({
                    'student_id': student.id,
                    'name': student.user.get_full_name(),
                    'attended': attended,
                    'total': total,
                    'rate': (attended / total * 100) if total > 0 else 0,
                })

            return Response(attendance_data)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def wallet_info(self, request):
        if request.user.role != 'teacher':
            return Response({'error': 'Only teachers can access this'}, status=status.HTTP_403_FORBIDDEN)

        try:
            teacher = request.user.teacher
            wallet = teacher.wallet
            wallet.update_balance()

            return Response({
                'balance': float(wallet.balance),
                'total_earned': float(wallet.total_earned),
                'total_paid': float(wallet.total_paid),
                'total_pending': float(wallet.total_pending),
            })
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def upcoming_lessons(self, request):
        if request.user.role != 'teacher':
            return Response({'error': 'Only teachers can access this'}, status=status.HTTP_403_FORBIDDEN)

        teacher = request.user.teacher
        now = datetime.now()

        lessons = Lesson.objects.filter(
            teacher=teacher,
            start_time__gte=now,
            is_cancelled=False
        ).order_by('start_time')[:10]

        lesson_data = []
        for lesson in lessons:
            lesson_data.append({
                'id': lesson.id,
                'group': lesson.group.name,
                'start_time': lesson.start_time,
                'duration': lesson.duration_minutes,
                'room': lesson.room,
                'online_link': lesson.online_link,
                'student_count': lesson.group.students.count(),
            })

        return Response(lesson_data)

# -----------------------
# Homework ViewSet
# -----------------------
class HomeworkViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'group__name']
    ordering_fields = ['due_date', 'created_date']

    def get_queryset(self):
        if self.request.user.role != 'teacher':
            return Homework.objects.none()
        teacher = self.request.user.teacher
        return Homework.objects.filter(teacher=teacher)

    def perform_create(self, serializer):
        teacher = self.request.user.teacher
        serializer.save(teacher=teacher)

# -----------------------
# Homework Submission
# -----------------------
class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSubmissionSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['submitted_date']

    def get_queryset(self):
        if self.request.user.role != 'teacher':
            return HomeworkSubmission.objects.none()
        teacher = self.request.user.teacher
        return HomeworkSubmission.objects.filter(homework__teacher=teacher)

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        submission = self.get_object()
        submission.grade = request.data.get('grade')
        submission.feedback = request.data.get('feedback', '')
        submission.save()

        submission.homework.status = 'graded'
        submission.homework.save()

        return Response({'status': 'Homework graded'})

# -----------------------
# Teacher Portfolio
# -----------------------
class TeacherPortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherPortfolioSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.role != 'teacher':
            return TeacherPortfolio.objects.none()
        teacher = self.request.user.teacher
        return TeacherPortfolio.objects.filter(teacher=teacher)

    def perform_create(self, serializer):
        teacher = self.request.user.teacher
        serializer.save(teacher=teacher)
