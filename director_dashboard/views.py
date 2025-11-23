from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, timedelta
from core.models import (
    Group, Lesson, Student, Teacher, CustomUser, Branch, Organization,
    Attendance, Payment
)
from finance.models import FinanceReport, TeacherPayment
from auth_system.permissions import IsDirector
import json

class DirectorDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsDirector]

    # ⚡ Swagger xatosini tuzatish uchun list metodini qo'shamiz
    def list(self, request):
        """Swagger va DRF uchun default endpoint"""
        return self.overview(request)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        user = request.user
        if user.role == 'superadmin':
            branches = Branch.objects.all()
        else:
            branches = user.organization.branches.all() if user.organization else []
        
        stats = {
            'total_students': Student.objects.filter(branch__in=branches).count(),
            'total_teachers': Teacher.objects.filter(branch__in=branches).count(),
            'active_groups': Group.objects.filter(branch__in=branches).count(),
            'total_branches': branches.count(),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def financial_overview(self, request):
        user = request.user
        if user.role == 'superadmin':
            branches = Branch.objects.all()
        else:
            branches = user.organization.branches.all() if user.organization else []
        
        today = datetime.today().date()
        month_start = today.replace(day=1)
        
        reports = FinanceReport.objects.filter(
            branch__in=branches,
            report_date__gte=month_start
        ).aggregate(
            total_income=Sum('total_student_payments'),
            total_expenses=Sum('teacher_payments') + Sum('staff_payments'),
            total_profit=Sum('profit')
        )
        
        return Response(reports)
    
    @action(detail=False, methods=['get'])
    def teacher_performance(self, request):
        user = request.user
        if user.role == 'superadmin':
            teachers = Teacher.objects.all()
        elif user.organization:
            teachers = Teacher.objects.filter(branch__organization=user.organization)
        else:
            teachers = Teacher.objects.filter(branch=user.branch)
        
        performance = []
        for teacher in teachers:
            lessons_count = Lesson.objects.filter(teacher=teacher).count()
            avg_attendance = Attendance.objects.filter(
                lesson__teacher=teacher
            ).values('status').annotate(count=Count('id'))
            
            performance.append({
                'teacher_id': teacher.id,
                'name': teacher.user.get_full_name(),
                'lessons': lessons_count,
                'rating': teacher.performance_rating,
                'total_earned': teacher.total_earned,
            })
        
        return Response(performance)
    
    @action(detail=False, methods=['get'])
    def group_statistics(self, request):
        user = request.user
        if user.role == 'superadmin':
            groups = Group.objects.all()
        elif user.organization:
            groups = Group.objects.filter(branch__organization=user.organization)
        else:
            groups = Group.objects.filter(branch=user.branch)
        
        stats = []
        for group in groups:
            student_count = group.students.count()
            avg_attendance = Attendance.objects.filter(
                lesson__group=group,
                status='present'
            ).count()
            total_lessons = Lesson.objects.filter(group=group).count()
            
            stats.append({
                'group_id': group.id,
                'name': group.name,
                'subject': group.subject,
                'students': student_count,
                'attendance_rate': (avg_attendance / total_lessons * 100) if total_lessons > 0 else 0,
                'teacher': group.teacher.user.get_full_name() if group.teacher else None,
            })
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def student_drop_rate(self, request):
        user = request.user
        if user.role == 'superadmin':
            students = Student.objects.all()
        elif user.organization:
            students = Student.objects.filter(branch__organization=user.organization)
        else:
            students = Student.objects.filter(branch=user.branch)
        
        days_range = int(request.query_params.get('days', 30))
        start_date = datetime.today().date() - timedelta(days=days_range)
        
        at_risk = []
        for student in students:
            absences = Attendance.objects.filter(
                student=student,
                status='absent',
                lesson__start_time__date__gte=start_date
            ).count()
            
            if absences > 5:
                at_risk.append({
                    'student_id': student.id,
                    'name': student.user.get_full_name(),
                    'absences': absences,
                    'risk_level': 'high' if absences > 10 else 'medium'
                })
        
        return Response(at_risk)
    
    @action(detail=False, methods=['post'])
    def create_branch(self, request):
        if request.user.role not in ['superadmin', 'director']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        branch = Branch.objects.create(
            organization=request.user.organization,
            name=data['name'],
            address=data['address'],
            phone=data['phone']
        )
        
        return Response({
            'id': branch.id,
            'name': branch.name,
            'status': 'created'
        })
    
    @action(detail=False, methods=['post'])
    def close_branch(self, request):
        branch_id = request.data.get('branch_id')
        if not branch_id:
            return Response({'error': 'branch_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            branch = Branch.objects.get(id=branch_id)
            branch.status = False
            branch.save()
            return Response({'status': 'Branch closed'})
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def monthly_trends(self, request):
        user = request.user
        months = int(request.query_params.get('months', 6))
        
        if user.role == 'superadmin':
            branches = Branch.objects.all()
        else:
            branches = user.organization.branches.all() if user.organization else []
        
        trends = []
        for i in range(months):
            date = datetime.today().date() - timedelta(days=30*i)
            month_start = date.replace(day=1)
            
            report = FinanceReport.objects.filter(
                branch__in=branches,
                report_date__month=month_start.month,
                report_date__year=month_start.year
            ).aggregate(
                income=Sum('total_student_payments'),
                expenses=Sum('teacher_payments') + Sum('staff_payments'),
                profit=Sum('profit')
            )
            
            trends.append({
                'month': month_start.strftime('%Y-%m'),
                **report
            })
        
        return Response(trends)
