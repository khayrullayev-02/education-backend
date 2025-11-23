# exams/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Q, Case, When, F, Avg, Max, Min
from datetime import datetime
from .models import Exam, ExamResult, ExamUpload, ExamGradeRange
from .serializers import (
    ExamSerializer, ExamResultSerializer, ExamUploadSerializer,
    ExamDetailedSerializer, ExamGradeRangeSerializer
)
from core.models import Group, Student
from auth_system.permissions import IsDirector, IsAdmin

class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'subject', 'group__name']
    ordering_fields = ['exam_date', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'superadmin':
            return Exam.objects.all()
        
        if user.role in ['director', 'manager', 'admin'] and user.branch:
            return Exam.objects.filter(group__branch=user.branch)
        
        if user.role == 'teacher':
            return Exam.objects.filter(group__teacher=user.teacher)
        
        if user.role == 'student':
            return Exam.objects.filter(group__in=user.student.groups.all())
        
        return Exam.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def detailed(self, request, pk=None):
        exam = self.get_object()
        serializer = ExamDetailedSerializer(exam)
        return Response(serializer.data)

class ExamResultViewSet(viewsets.ModelViewSet):
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['score', 'grade', 'submitted_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'superadmin':
            return ExamResult.objects.all()
        
        if user.role in ['director', 'manager', 'admin'] and user.branch:
            return ExamResult.objects.filter(exam__group__branch=user.branch)
        
        if user.role == 'teacher':
            return ExamResult.objects.filter(exam__group__teacher=user.teacher)
        
        if user.role == 'student':
            return ExamResult.objects.filter(student__user=user)
        
        return ExamResult.objects.none()
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        if request.user.role not in ['director', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        exam_id = request.data.get('exam_id')
        results_data = request.data.get('results', [])
        
        try:
            exam = Exam.objects.get(id=exam_id)
            created_count = 0
            
            for result_data in results_data:
                try:
                    student = Student.objects.get(id=result_data['student_id'])
                    score = result_data['score']
                    
                    grade_range = ExamGradeRange.objects.filter(
                        min_score__lte=score,
                        max_score__gte=score
                    ).first()
                    
                    if grade_range:
                        ExamResult.objects.update_or_create(
                            exam=exam,
                            student=student,
                            defaults={'score': score, 'grade': grade_range.grade}
                        )
                        created_count += 1
                except Student.DoesNotExist:
                    continue
            
            return Response({'status': 'imported', 'count': created_count})
        except Exam.DoesNotExist:
            return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def by_grade(self, request):
        exam_id = request.query_params.get('exam')
        if not exam_id:
            return Response({'error': 'exam parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = self.get_queryset().filter(exam__id=exam_id).values('grade').annotate(count=Count('id'))
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        exam_id = request.query_params.get('exam')
        if not exam_id:
            return Response({'error': 'exam parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = self.get_queryset().filter(exam__id=exam_id)
        
        stats = {
            'total_students': results.count(),
            'average_score': results.aggregate(avg=Avg('score'))['avg'] or 0,
            'highest_score': results.aggregate(max=Max('score'))['max'] or 0,
            'lowest_score': results.aggregate(min=Min('score'))['min'] or 0,
            'passed': results.filter(score__gte=F('exam__pass_score')).count(),
            'failed': results.filter(score__lt=F('exam__pass_score')).count(),
        }
        
        return Response(stats)

class ExamUploadViewSet(viewsets.ModelViewSet):
    serializer_class = ExamUploadSerializer
    # permission_classes = [IsAdmin]
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['uploaded_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return ExamUpload.objects.all()
        if user.branch:
            return ExamUpload.objects.filter(exam__group__branch=user.branch)
        return ExamUpload.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
