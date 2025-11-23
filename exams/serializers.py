from rest_framework import serializers
from .models import Exam, ExamResult, ExamUpload, ExamGradeRange
from core.models import Group

class ExamGradeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamGradeRange
        fields = ['id', 'grade', 'min_score', 'max_score', 'description']

class ExamSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    results_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ['id', 'group', 'group_name', 'title', 'subject', 'exam_date',
                  'total_questions', 'total_points', 'pass_score', 'created_by',
                  'created_by_name', 'results_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_results_count(self, obj):
        return obj.results.count()

class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    
    class Meta:
        model = ExamResult
        fields = ['id', 'exam', 'exam_title', 'student', 'student_name', 'score', 'grade', 'submitted_at']
        read_only_fields = ['submitted_at']

class ExamUploadSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = ExamUpload
        fields = ['id', 'exam', 'exam_title', 'file', 'file_format', 'uploaded_at', 'uploaded_by', 'uploaded_by_name']
        read_only_fields = ['uploaded_at']

class ExamDetailedSerializer(serializers.ModelSerializer):
    results = ExamResultSerializer(many=True, read_only=True)
    uploaded_files = ExamUploadSerializer(many=True, read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = Exam
        fields = ['id', 'group', 'group_name', 'title', 'subject', 'exam_date',
                  'total_questions', 'total_points', 'pass_score', 'created_at',
                  'results', 'uploaded_files']
