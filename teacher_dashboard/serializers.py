from rest_framework import serializers
from .models import Homework, HomeworkSubmission, TeacherPortfolio
from core.models import Group, Attendance, Lesson

class HomeworkSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    submitted_count = serializers.SerializerMethodField()
    graded_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Homework
        fields = ['id', 'group', 'group_name', 'title', 'description', 'file',
                  'due_date', 'status', 'created_date', 'submitted_count', 'graded_count']
    
    def get_submitted_count(self, obj):
        return obj.submissions.count()
    
    def get_graded_count(self, obj):
        return obj.submissions.filter(grade__isnull=False).count()

class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    homework_title = serializers.CharField(source='homework.title', read_only=True)
    
    class Meta:
        model = HomeworkSubmission
        fields = ['id', 'homework', 'homework_title', 'student', 'student_name',
                  'file', 'submitted_date', 'grade', 'feedback']

class TeacherPortfolioSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    
    class Meta:
        model = TeacherPortfolio
        fields = ['id', 'teacher', 'teacher_name', 'bio', 'achievements',
                  'total_students_taught', 'avg_rating', 'created_at', 'updated_at']
        read_only_fields = ['total_students_taught', 'avg_rating', 'created_at', 'updated_at']
