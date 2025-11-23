from rest_framework import serializers
from .models import (
    FinanceReport, StudentPayment, TeacherPayment, StaffPayment,
    Wallet, PaymentDiscount, IncomeLead
)
from core.models import Teacher

class FinanceReportSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = FinanceReport
        fields = ['id', 'branch', 'branch_name', 'report_date', 'report_type',
                  'total_student_payments', 'teacher_payments', 'staff_payments',
                  'other_expenses', 'profit', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'profit']

class StudentPaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = StudentPayment
        fields = ['id', 'student', 'student_name', 'branch', 'amount', 'payment_method',
                  'receipt_number', 'receipt_file', 'status', 'approved_by', 'approved_by_name',
                  'notes', 'paid_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TeacherPaymentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = TeacherPayment
        fields = ['id', 'teacher', 'teacher_name', 'branch', 'month', 'hourly_amount',
                  'group_amount', 'bonus', 'penalty', 'total_amount', 'status',
                  'approved_by', 'approved_by_name', 'paid_date', 'payment_method',
                  'notes', 'created_at', 'updated_at']
        read_only_fields = ['total_amount', 'created_at', 'updated_at']

class StaffPaymentSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff_member.get_full_name', read_only=True)
    
    class Meta:
        model = StaffPayment
        fields = ['id', 'staff_member', 'staff_name', 'branch', 'month', 'position',
                  'salary', 'bonus', 'penalty', 'total_amount', 'status', 'paid_date', 'created_at']
        read_only_fields = ['total_amount', 'created_at']

class WalletSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'teacher', 'teacher_name', 'balance', 'total_earned',
                  'total_paid', 'total_pending', 'updated_at']
        read_only_fields = ['balance', 'total_earned', 'total_paid', 'total_pending', 'updated_at']

class PaymentDiscountSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    applied_by_name = serializers.CharField(source='applied_by.get_full_name', read_only=True)
    
    class Meta:
        model = PaymentDiscount
        fields = ['id', 'student', 'student_name', 'branch', 'discount_type', 'value',
                  'reason', 'applied_by', 'applied_by_name', 'created_at']
        read_only_fields = ['created_at']

class IncomeLeadSerializer(serializers.ModelSerializer):
    converted_student_name = serializers.CharField(source='converted_student.user.get_full_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = IncomeLead
        fields = ['id', 'branch', 'branch_name', 'name', 'email', 'phone', 'source',
                  'status', 'converted_student', 'converted_student_name', 'notes',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
