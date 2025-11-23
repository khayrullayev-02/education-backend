from django.db import models
from core.models import Teacher, Student, Branch, Group, Lesson, CustomUser
import uuid

class GroupManagement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    managed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    teacher_reassignments = models.IntegerField(default=0)
    student_transfers = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

class PerformanceMetrics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    metric_date = models.DateField()
    total_lessons = models.IntegerField(default=0)
    completed_lessons = models.IntegerField(default=0)
    cancelled_lessons = models.IntegerField(default=0)
    avg_attendance_rate = models.FloatField(default=0)
    avg_teacher_punctuality = models.FloatField(default=0)

class NotificationAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('teacher_late', 'Teacher Late'),
        ('student_absent', 'Student Absent'),
        ('lesson_cancelled', 'Lesson Cancelled'),
        ('payment_due', 'Payment Due'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    related_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
