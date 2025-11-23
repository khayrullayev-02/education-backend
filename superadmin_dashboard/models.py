from django.db import models
from core.models import CustomUser, Organization

class SuperadminAuditLog(models.Model):
    superadmin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    class Meta:
        app_label = 'superadmin_dashboard'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.superadmin} - {self.action}"


class OrganizationSettings(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    max_branches = models.IntegerField(default=10)
    max_students_per_group = models.IntegerField(default=30)
    subscription_type = models.CharField(
        max_length=50,
        choices=[('free', 'Free'), ('pro', 'Pro'), ('enterprise', 'Enterprise')],
        default='free'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'superadmin_dashboard'

    def __str__(self):
        return f"{self.organization.name} - {self.subscription_type}"


class SubscriptionType(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=50, choices=SUBSCRIPTION_CHOICES, unique=True)
    max_branches = models.IntegerField(default=1)
    max_students = models.IntegerField(default=100)
    max_teachers = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'superadmin_dashboard'

    def __str__(self):
        return self.name
