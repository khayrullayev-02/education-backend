from django.db import models
from core.models import Organization, Branch, CustomUser
import uuid


class LoyaltyBranch(models.Model):
    """Loyalty program branches management"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.OneToOneField(Branch, on_delete=models.CASCADE, related_name='loyalty_branch')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='loyalty_branches')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    points_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    min_purchase_for_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_primary = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_loyalty_branches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('branch', 'organization')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.branch.name}"


class LoyaltyPoint(models.Model):
    """Track loyalty points for customers/students"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loyalty_branch = models.ForeignKey(LoyaltyBranch, on_delete=models.CASCADE, related_name='points')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='loyalty_points')
    points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    points_redeemed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('loyalty_branch', 'user')
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.total_points} pts"
