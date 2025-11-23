from rest_framework import serializers
from .models import Notification, NotificationTemplate, EmailTemplate, NotificationLog

class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer for managing user notifications"""
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 
                  'status', 'is_read', 'created_at', 'sent_at']
        read_only_fields = ['created_at', 'sent_at', 'status']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Template for notification messages"""
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'subject', 'template_text', 'created_at']


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Email template serializer with variables support"""
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'variables', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Notification log for tracking sent notifications"""
    class Meta:
        model = NotificationLog
        fields = ['id', 'user', 'notification_type', 'recipient', 'subject', 'message', 
                  'status', 'error_message', 'created_at', 'sent_at']
        read_only_fields = ['created_at', 'sent_at']
