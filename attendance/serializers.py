from rest_framework import serializers
from core.models import Attendance, Lesson, Student, Group
from datetime import datetime

class AttendanceSheetSerializer(serializers.Serializer):
    lesson_id = serializers.UUIDField()
    students_attendance = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    teacher_status = serializers.ChoiceField(choices=['present', 'absent', 'late'])

class BulkAttendanceSerializer(serializers.Serializer):
    lesson_id = serializers.UUIDField()
    attendance_records = serializers.ListField(
        child=serializers.DictField()
    )

class AttendanceDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    lesson_info = serializers.SerializerMethodField()
    
    class Meta:
        from core.models import Attendance
        model = Attendance
        fields = ['id', 'student', 'student_name', 'lesson', 'lesson_info', 'status',
                  'homework_status', 'homework_grade', 'comments', 'teacher_comments', 'submitted_at']
    
    def get_lesson_info(self, obj):
        return {
            'group': obj.lesson.group.name,
            'subject': obj.lesson.group.subject,
            'start_time': obj.lesson.start_time,
            'teacher': obj.lesson.teacher.user.get_full_name(),
        }
