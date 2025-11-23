from rest_framework import serializers
from .models import SuperadminAuditLog, OrganizationSettings, SubscriptionType
from core.models import User, Organization

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


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = ['id', 'name', 'max_branches', 'max_students', 'max_teachers', 'price', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class SuperadminOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'address', 'phone', 'email', 'created_at', 'is_active']
        read_only_fields = ['created_at']


class SuperadminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']
