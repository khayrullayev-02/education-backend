from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from .models import (
    FinanceReport, StudentPayment, TeacherPayment, StaffPayment,
    Wallet, PaymentDiscount, IncomeLead
)
from .serializers import (
    FinanceReportSerializer, StudentPaymentSerializer, TeacherPaymentSerializer,
    StaffPaymentSerializer, WalletSerializer, PaymentDiscountSerializer,
    IncomeLeadSerializer
)
from auth_system.permissions import IsDirector, IsManager, IsAdmin

class FinanceReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FinanceReportSerializer
    permission_classes = [IsDirector]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['branch__name']
    ordering_fields = ['report_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return FinanceReport.objects.all()
        if user.branch:
            return FinanceReport.objects.filter(branch=user.branch)
        return FinanceReport.objects.none()
    
    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        today = datetime.today().date()
        reports = self.get_queryset().filter(report_date=today)
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly_report(self, request):
        today = datetime.today().date()
        week_start = today - timedelta(days=today.weekday())
        reports = self.get_queryset().filter(report_date__gte=week_start, report_date__lte=today)
        total = reports.aggregate(
            total_payments=Sum('total_student_payments'),
            teacher_payments=Sum('teacher_payments'),
            profit=Sum('profit')
        )
        return Response(total)
    
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        today = datetime.today().date()
        month_start = today.replace(day=1)
        reports = self.get_queryset().filter(report_date__gte=month_start, report_date__lte=today)
        total = reports.aggregate(
            total_payments=Sum('total_student_payments'),
            teacher_payments=Sum('teacher_payments'),
            staff_payments=Sum('staff_payments'),
            expenses=Sum('other_expenses'),
            profit=Sum('profit')
        )
        return Response(total)

class StudentPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentPaymentSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'receipt_number']
    ordering_fields = ['created_at', 'amount']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return StudentPayment.objects.all()
        if user.branch:
            return StudentPayment.objects.filter(branch=user.branch)
        return StudentPayment.objects.none()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        payments = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_income(self, request):
        today = datetime.today().date()
        payments = self.get_queryset().filter(
            status='completed',
            paid_at__date=today
        ).aggregate(total=Sum('amount'))
        return Response(payments)
    
    @action(detail=False, methods=['get'])
    def debtors(self, request):
        from core.models import Student
        debtors = Student.objects.filter(total_debt__gt=0)
        return Response({
            'count': debtors.count(),
            'total_debt': debtors.aggregate(Sum('total_debt'))
        })
    
    @action(detail=['post'], methods=['post'])
    def approve(self, request, pk=None):
        payment = self.get_object()
        if payment.status != 'pending':
            return Response({'error': 'Payment is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        payment.status = 'completed'
        payment.approved_by = request.user
        payment.paid_at = datetime.now()
        payment.save()
        return Response({'status': 'Payment approved'})

class TeacherPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherPaymentSerializer
    permission_classes = [IsDirector]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name']
    ordering_fields = ['month', 'total_amount']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return TeacherPayment.objects.all()
        if user.branch:
            return TeacherPayment.objects.filter(branch=user.branch)
        return TeacherPayment.objects.none()
    
    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        payments = self.get_queryset().filter(status='pending')
        total = payments.aggregate(Sum('total_amount'))
        serializer = self.get_serializer(payments, many=True)
        return Response({'count': payments.count(), 'total': total, 'payments': serializer.data})
    
    @action(detail=['post'], methods=['post'])
    def approve(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'approved'
        payment.approved_by = request.user
        payment.save()
        return Response({'status': 'Payment approved'})
    
    @action(detail=['post'], methods=['post'])
    def mark_paid(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'paid'
        payment.paid_date = datetime.today().date()
        payment.save()
        payment.teacher.wallet.update_balance()
        return Response({'status': 'Payment marked as paid'})

class StaffPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = StaffPaymentSerializer
    permission_classes = [IsDirector]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['month', 'total_amount']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return StaffPayment.objects.all()
        if user.branch:
            return StaffPayment.objects.filter(branch=user.branch)
        return StaffPayment.objects.none()
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        month = request.query_params.get('month')
        branch = request.query_params.get('branch')
        
        query = self.get_queryset()
        if month:
            query = query.filter(month=month)
        if branch:
            query = query.filter(branch=branch)
        
        summary = query.aggregate(
            total_salary=Sum('salary'),
            total_bonus=Sum('bonus'),
            total_penalty=Sum('penalty'),
            total_paid=Sum('total_amount', filter=Q(status='paid'))
        )
        return Response(summary)

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return Wallet.objects.filter(teacher__user=user)
        if user.role in ['superadmin', 'director', 'manager']:
            if user.branch:
                return Wallet.objects.filter(teacher__branch=user.branch)
            return Wallet.objects.all()
        return Wallet.objects.none()
    
    @action(detail=['get'], methods=['get'])
    def balance(self, request, pk=None):
        wallet = self.get_object()
        wallet.update_balance()
        return Response(self.get_serializer(wallet).data)

class PaymentDiscountViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentDiscountSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return PaymentDiscount.objects.all()
        if user.branch:
            return PaymentDiscount.objects.filter(branch=user.branch)
        return PaymentDiscount.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(applied_by=self.request.user)

class IncomeLeadViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeLeadSerializer
    permission_classes = [IsManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'source']
    ordering_fields = ['created_at', 'source']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return IncomeLead.objects.all()
        if user.branch:
            return IncomeLead.objects.filter(branch=user.branch)
        return IncomeLead.objects.none()
    
    @action(detail=False, methods=['get'])
    def conversion_stats(self, request):
        query = self.get_queryset()
        stats = {
            'total_leads': query.count(),
            'new': query.filter(status='new').count(),
            'contacted': query.filter(status='contacted').count(),
            'enrolled': query.filter(status='enrolled').count(),
            'rejected': query.filter(status='rejected').count(),
            'conversion_rate': (query.filter(status='enrolled').count() / query.count() * 100) if query.count() > 0 else 0
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def by_source(self, request):
        query = self.get_queryset()
        sources = query.values('source').annotate(count=Count('id')).order_by('-count')
        return Response(sources)
