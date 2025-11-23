# statistics_app/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Sum, Avg
from datetime import datetime, timedelta
from core.models import Student, Teacher, Group, Attendance
from exams.models import ExamResult
from finance.models import FinanceReport
from auth_system.permissions import IsDirector, IsManager

class StatisticsViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def student_statistics(self, request):
        user = request.user
        
        if user.role == 'superadmin':
            students = Student.objects.all()
        elif getattr(user, 'organization', None):
            students = Student.objects.filter(branch__organization=user.organization)
        else:
            students = Student.objects.filter(branch=user.branch) if user.branch else Student.objects.none()
        
        stats = {
            'total_students': students.count(),
            'active': students.filter(status='active').count(),
            'inactive': students.filter(status='inactive').count(),
            'graduated': students.filter(status='graduated').count(),
            'avg_payment_debt': students.aggregate(Avg('total_debt'))['total_debt__avg'] or 0,
            'total_debt': students.aggregate(Sum('total_debt'))['total_debt__sum'] or 0,
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def teacher_statistics(self, request):
        user = request.user
        
        if user.role == 'superadmin':
            teachers = Teacher.objects.all()
        elif getattr(user, 'organization', None):
            teachers = Teacher.objects.filter(branch__organization=user.organization)
        else:
            teachers = Teacher.objects.filter(branch=user.branch) if user.branch else Teacher.objects.none()
        
        avg_rating = teachers.aggregate(Avg('performance_rating'))['performance_rating__avg'] or 0
        
        stats = {
            'total_teachers': teachers.count(),
            'avg_rating': round(avg_rating, 2),
            'top_teachers': teachers.order_by('-performance_rating').values(
                'user__first_name', 'user__last_name', 'performance_rating'
            )[:5],
            'total_earned': teachers.aggregate(Sum('total_earned'))['total_earned__sum'] or 0,
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def attendance_statistics(self, request):
        branch = request.user.branch
        period_days = int(request.query_params.get('days', 30))
        start_date = datetime.today().date() - timedelta(days=period_days)
        
        attendance = Attendance.objects.filter(
            lesson__branch=branch,
            lesson__start_time__date__gte=start_date
        )
        
        stats = {
            'total_records': attendance.count(),
            'present': attendance.filter(status='present').count(),
            'absent': attendance.filter(status='absent').count(),
            'late': attendance.filter(status='late').count(),
            'excused': attendance.filter(status='excused').count(),
        }
        
        if stats['total_records'] > 0:
            stats['attendance_rate'] = round((stats['present'] / stats['total_records']) * 100, 2)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def financial_statistics(self, request):
        branch = request.user.branch
        period_days = int(request.query_params.get('days', 30))
        start_date = datetime.today().date() - timedelta(days=period_days)
        
        if not branch:
            return Response({'error': 'Branch not found'}, status=400)
        
        reports = FinanceReport.objects.filter(
            branch=branch,
            report_date__gte=start_date
        ).aggregate(
            total_income=Sum('total_student_payments'),
            total_teacher_expenses=Sum('teacher_payments'),
            total_staff_expenses=Sum('staff_payments'),
            total_other_expenses=Sum('other_expenses'),
            total_profit=Sum('profit')
        )
        
        return Response(reports)
    
    @action(detail=False, methods=['get'])
    def exam_statistics(self, request):
        user = request.user
        
        if user.role == 'superadmin':
            results = ExamResult.objects.all()
        elif getattr(user, 'organization', None):
            results = ExamResult.objects.filter(exam__group__branch__organization=user.organization)
        else:
            results = ExamResult.objects.filter(exam__group__branch=user.branch) if user.branch else ExamResult.objects.none()
        
        stats = {
            'total_exams': results.values('exam').distinct().count(),
            'total_results': results.count(),
            'average_score': round(results.aggregate(Avg('score'))['score__avg'] or 0, 2),
            'grade_distribution': results.values('grade').annotate(count=Count('id')),
            'highest_score': results.aggregate(max_score=Max('score'))['max_score'] or 0,
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def group_statistics(self, request):
        user = request.user
        
        if user.role == 'superadmin':
            groups = Group.objects.all()
        elif getattr(user, 'organization', None):
            groups = Group.objects.filter(branch__organization=user.organization)
        else:
            groups = Group.objects.filter(branch=user.branch) if user.branch else Group.objects.none()
        
        group_stats = []
        for group in groups:
            student_count = group.students.count()
            attendance_records = Attendance.objects.filter(lesson__group=group)
            present_rate = (
                attendance_records.filter(status='present').count() / attendance_records.count() * 100
                if attendance_records.count() > 0 else 0
            )
            
            group_stats.append({
                'group_id': group.id,
                'name': group.name,
                'subject': group.subject,
                'students': student_count,
                'teacher': group.teacher.user.get_full_name() if group.teacher else None,
                'attendance_rate': round(present_rate, 2),
            })
        
        return Response(group_stats)
