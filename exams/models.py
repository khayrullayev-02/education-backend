from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Group, Student, CustomUser
import uuid

class ExamGradeRange(models.Model):
    GRADE_CHOICES = [
        ('A', 'Excellent (86-100)'),
        ('B', 'Good (51-85)'),
        ('C', 'Poor (0-50)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, unique=True)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.grade} ({self.min_score}-{self.max_score})"

class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    exam_date = models.DateTimeField()
    total_questions = models.IntegerField()
    total_points = models.IntegerField(default=100)
    pass_score = models.IntegerField(default=50)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.group.name}"

class ExamResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])
    grade = models.CharField(
        max_length=1, 
        choices=ExamGradeRange._meta.get_field('grade').choices
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('exam', 'student')
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam.title}: {self.score}"

class ExamUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='exams/%Y/%m/%d/')
    file_format = models.CharField(max_length=20, choices=[
        ('excel', 'Excel'),
        ('word', 'Word'),
        ('pdf', 'PDF'),
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.exam.title} - {self.file_format}"
