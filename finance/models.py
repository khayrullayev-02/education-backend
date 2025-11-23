from django.db import models
from core.models import Teacher, Student, Branch, CustomUser
from django.db.models import Sum
import uuid

class FinanceReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='finance_reports')
    report_date = models.DateField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='daily')
    total_student_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    teacher_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    staff_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_profit(self):
        total_expenses = self.teacher_payments + self.staff_payments + self.other_expenses
        self.profit = self.total_student_payments - total_expenses
        self.save()
    
    def __str__(self):
        return f"Finance Report - {self.branch.name} - {self.report_date}"
    
    class Meta:
        unique_together = ('branch', 'report_date', 'report_type')
        ordering = ['-report_date']

class StudentPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_records')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_file = models.FileField(upload_to='receipts/%Y/%m/%d/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payments')
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.amount}"
    
    class Meta:
        ordering = ['-created_at']

class TeacherPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='salary_payments')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    month = models.DateField()
    hourly_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    group_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_teacher_payments')
    paid_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('wallet', 'Wallet'),
    ], default='bank')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self):
        self.total_amount = self.hourly_amount + self.group_amount + self.bonus - self.penalty
        self.save()
    
    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.month}"
    
    class Meta:
        unique_together = ('teacher', 'branch', 'month')
        ordering = ['-month']

class StaffPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ]
    
    POSITION_CHOICES = [
        ('manager', 'Manager'),
        ('admin', 'Admin'),
        ('support', 'Support'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='staff_payments')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    month = models.DateField()
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_total(self):
        self.total_amount = self.salary + self.bonus - self.penalty
        self.save()
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.month}"

class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pending = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def update_balance(self):
        total_payments = self.teacher.salary_payments.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        self.total_paid = total_payments
        self.balance = self.total_earned - self.total_paid
        self.save()
    
    def __str__(self):
        return f"Wallet - {self.teacher.user.get_full_name()}"

class PaymentDiscount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='discounts')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    applied_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Discount for {self.student.user.get_full_name()}"

class IncomeLead(models.Model):
    SOURCE_CHOICES = [
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('enrolled', 'Enrolled'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='leads')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    converted_student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.source}"
    
    class Meta:
        ordering = ['-created_at']
