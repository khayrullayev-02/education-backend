from rest_framework import serializers
from .models import DocumentApproval, LessonMaterial, ExamAnswer, AttendanceCorrection
from core.models import Student, Group, Lesson

class StudentDetailSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    
    class Meta:
        from core.models import Student
        model = Student
        fields = ['id', 'user_details', 'branch', 'parent_email', 'parent_phone',
                  'status', 'enrollment_date', 'total_paid', 'total_debt', 'groups']
    
    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.get_full_name(),
            'email': obj.user.email,
            'phone': obj.user.phone,
            'date_of_birth': obj.user.date_of_birth,
            'profile_image': obj.user.profile_image.url if obj.user.profile_image else None,
        }
    
    def get_groups(self, obj):
        return [{'id': g.id, 'name': g.name, 'subject': g.subject} for g in obj.groups.all()]

class DocumentApprovalSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentApproval
        fields = ['id', 'student', 'student_name', 'document_type', 'file', 'status',
                  'approved_by', 'approved_by_name', 'rejection_reason', 'uploaded_at', 'approved_at']
        read_only_fields = ['uploaded_at', 'approved_at']

class LessonMaterialSerializer(serializers.ModelSerializer):
    lesson_info = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = LessonMaterial
        fields = ['id', 'lesson', 'lesson_info', 'title', 'description', 'file', 'file_type',
                  'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def get_lesson_info(self, obj):
        return {
            'id': obj.lesson.id,
            'group': obj.lesson.group.name,
            'start_time': obj.lesson.start_time,
        }

class ExamAnswerSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = ExamAnswer
        fields = ['id', 'exam', 'exam_title', 'file', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class AttendanceCorrectionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='original_attendance.student.user.get_full_name', read_only=True)
    corrected_by_name = serializers.CharField(source='corrected_by.get_full_name', read_only=True)
    
    class Meta:
        model = AttendanceCorrection
        fields = ['id', 'original_attendance', 'student_name', 'old_status', 'new_status',
                  'reason', 'corrected_by', 'corrected_by_name', 'corrected_at']
        read_only_fields = ['corrected_at']
