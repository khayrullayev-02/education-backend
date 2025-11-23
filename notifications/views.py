from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdmin
from .models import Notification, NotificationTemplate, EmailTemplate, NotificationLog
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer,
    EmailTemplateSerializer, NotificationLogSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'unread_count': 0})
        count = Notification.objects.filter(user=user, is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=False, methods=['get'])
    def active_templates(self, request):
        templates = EmailTemplate.objects.filter(is_active=True)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        template = self.get_object()
        template.is_active = not template.is_active
        template.save()
        serializer = self.get_serializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationLogViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return NotificationLog.objects.none()
        if user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin']:
            return NotificationLog.objects.all()
        return NotificationLog.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def recent_logs(self, request):
        logs = self.get_queryset().order_by('-created_at')[:100]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def failed_notifications(self, request):
        logs = self.get_queryset().filter(status='failed')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def retry_send(self, request, pk=None):
        log = self.get_object()
        log.status = 'pending'
        log.error_message = None
        log.save()
        serializer = self.get_serializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)
