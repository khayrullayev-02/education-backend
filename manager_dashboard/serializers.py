from rest_framework import serializers
from .models import PerformanceMetrics, NotificationAlert
from core.models import Group, Teacher, Student

class GroupTransferSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    from_group_id = serializers.UUIDField()
    to_group_id = serializers.UUIDField()
    reason = serializers.CharField()

class TeacherReassignmentSerializer(serializers.Serializer):
    group_id = serializers.UUIDField()
    old_teacher_id = serializers.UUIDField()
    new_teacher_id = serializers.UUIDField()
    reason = serializers.CharField()

class PerformanceMetricsSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceMetrics
        fields = ['id', 'branch', 'branch_name', 'metric_date', 'total_lessons',
                  'completed_lessons', 'cancelled_lessons', 'avg_attendance_rate',
                  'avg_teacher_punctuality', 'completion_rate']
    
    def get_completion_rate(self, obj):
        if obj.total_lessons == 0:
            return 0
        return (obj.completed_lessons / obj.total_lessons) * 100

class NotificationAlertSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = NotificationAlert
        fields = ['id', 'branch', 'branch_name', 'alert_type', 'message',
                  'is_processed', 'created_at']
        read_only_fields = ['created_at']
