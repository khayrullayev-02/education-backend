from django.db import models
from core.models import CustomUser, Student

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Wallet'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'payments'

    def __str__(self):
        return f"{self.student.full_name} - {self.payment_type}"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    reference_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.reference_id} - {self.amount}"


class PaymentInitiation(models.Model):
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('click', 'Click'),
        ('payme', 'Payme'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_initiations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    payment_gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    callback_url = models.URLField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"PaymentInit {self.id} - {self.student.full_name}"
