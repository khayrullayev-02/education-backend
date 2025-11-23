# attendance/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from datetime import datetime, timedelta
from core.models import Attendance, Lesson, Group, Student, Teacher
from .serializers import AttendanceSheetSerializer, BulkAttendanceSerializer, AttendanceDetailSerializer
from auth_system.permissions import IsTeacher, IsAdmin

class AttendanceSubmissionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def submit_attendance(self, request):
        if request.user.role not in ['teacher', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AttendanceSheetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            lesson = Lesson.objects.get(id=serializer.validated_data['lesson_id'])
            
            created_count = 0
            for record in serializer.validated_data['students_attendance']:
                student = Student.objects.get(id=record['student_id'])
                
                attendance, created = Attendance.objects.update_or_create(
                    lesson=lesson,
                    student=student,
                    defaults={
                        'status': record['status'],
                        'homework_status': record.get('homework_status', 'missing'),
                        'homework_grade': record.get('homework_grade'),
                        'comments': record.get('comments', ''),
                    }
                )
                
                if created:
                    created_count += 1
            
            return Response({
                'status': 'Attendance submitted',
                'created': created_count,
                'total': len(serializer.validated_data['students_attendance'])
            })
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def select_all_present(self, request):
        lesson_id = request.query_params.get('lesson')
        if not lesson_id:
            return Response({'error': 'lesson parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            students = lesson.group.students.all()
            
            for student in students:
                Attendance.objects.update_or_create(
                    lesson=lesson,
                    student=student,
                    defaults={'status': 'present'}
                )
            
            return Response({'status': f'All {students.count()} students marked present'})
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['submitted_at', 'status']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'teacher':
            teacher = user.teacher
            return Attendance.objects.filter(lesson__teacher=teacher)
        
        if user.role == 'student':
            student = user.student
            return Attendance.objects.filter(student=student)
        
        if user.role == 'admin' and user.branch:
            return Attendance.objects.filter(lesson__branch=user.branch)
        
        if user.role == 'superadmin':
            return Attendance.objects.all()
        
        return Attendance.objects.none()
    
    @action(detail=False, methods=['get'])
    def pending_submission(self, request):
        today = datetime.today().date()
        lessons = Lesson.objects.filter(
            start_time__date=today,
            is_cancelled=False
        )
        
        pending = []
        for lesson in lessons:
            expected_count = lesson.group.students.count()
            submitted_count = Attendance.objects.filter(lesson=lesson).count()
            
            if submitted_count < expected_count:
                pending.append({
                    'lesson_id': lesson.id,
                    'group': lesson.group.name,
                    'submitted': submitted_count,
                    'expected': expected_count,
                    'remaining': expected_count - submitted_count,
                })
        
        return Response(pending)
