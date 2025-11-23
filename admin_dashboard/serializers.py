from rest_framework import serializers
from .models import DocumentApproval, LessonMaterial, ExamAnswer, AttendanceCorrection
from core.models import Student, Group, Lesson

class StudentDetailSerializer(serializers.ModelSerializer):
    """Serializer for Student details with relationships"""
    user_details = serializers.SerializerMethodField(help_text="User information including name, email, phone")
    groups = serializers.SerializerMethodField(help_text="List of groups student is enrolled in")
    
    class Meta:
        from core.models import Student
        model = Student
        fields = ['id', 'user_details', 'branch', 'parent_email', 'parent_phone',
                  'status', 'enrollment_date', 'total_paid', 'total_debt', 'groups']
        field_descriptions = {
            'branch': 'Branch where student is studying',
            'parent_email': 'Email of student parent/guardian',
            'parent_phone': 'Phone of student parent/guardian',
            'status': 'Student status (active, inactive, graduated)',
            'enrollment_date': 'Date student enrolled',
            'total_paid': 'Total amount paid by student',
            'total_debt': 'Total outstanding debt',
        }
    
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
    """Serializer for document approval workflow"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True, help_text="Full name of student")
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, help_text="Name of admin who approved")
    
    class Meta:
        model = DocumentApproval
        fields = ['id', 'student', 'student_name', 'document_type', 'file', 'status',
                  'approved_by', 'approved_by_name', 'rejection_reason', 'uploaded_at', 'approved_at']
        read_only_fields = ['uploaded_at', 'approved_at']

class LessonMaterialSerializer(serializers.ModelSerializer):
    """Serializer for lesson materials (PDFs, notes, resources)"""
    lesson_info = serializers.SerializerMethodField(help_text="Related lesson information")
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True, help_text="Teacher who uploaded")
    
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
    """Serializer for exam answers submitted by students"""
    exam_title = serializers.CharField(source='exam.title', read_only=True, help_text="Title of exam")
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True, help_text="Student who uploaded")
    
    class Meta:
        model = ExamAnswer
        fields = ['id', 'exam', 'exam_title', 'file', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class AttendanceCorrectionSerializer(serializers.ModelSerializer):
    """Serializer for attendance corrections by admins"""
    student_name = serializers.CharField(source='original_attendance.student.user.get_full_name', read_only=True, help_text="Student name")
    corrected_by_name = serializers.CharField(source='corrected_by.get_full_name', read_only=True, help_text="Admin who corrected")
    
    class Meta:
        model = AttendanceCorrection
        fields = ['id', 'original_attendance', 'student_name', 'old_status', 'new_status',
                  'reason', 'corrected_by', 'corrected_by_name', 'corrected_at']
        read_only_fields = ['corrected_at']
