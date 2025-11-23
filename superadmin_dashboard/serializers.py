from rest_framework import serializers
from .models import SuperadminAuditLog, OrganizationSettings

class SuperadminAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperadminAuditLog
        fields = ['id', 'superadmin', 'action', 'timestamp', 'details']
        read_only_fields = ['timestamp']


class OrganizationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSettings
        fields = ['id', 'organization', 'max_branches', 'max_students_per_group',
                  'subscription_type', 'is_active', 'created_at']
        read_only_fields = ['created_at']
