from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperadmin
from core.models import User, Organization
from .models import SuperadminAuditLog, OrganizationSettings, SubscriptionType
from .serializers import (
    SuperadminAuditLogSerializer, OrganizationSettingsSerializer, 
    SubscriptionTypeSerializer, SuperadminOrganizationSerializer, 
    SuperadminUserSerializer
)


class SuperadminAuditLogViewSet(viewsets.ModelViewSet):
    queryset = SuperadminAuditLog.objects.all()
    serializer_class = SuperadminAuditLogSerializer
    permission_classes = [IsAuthenticated, IsSuperadmin]

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        logs = SuperadminAuditLog.objects.all()[:50]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class OrganizationSettingsViewSet(viewsets.ModelViewSet):
    queryset = OrganizationSettings.objects.all()
    serializer_class = OrganizationSettingsSerializer
    permission_classes = [IsAuthenticated, IsSuperadmin]

    @action(detail=False, methods=['post'])
    def update_subscription(self, request):
        organization_id = request.data.get('organization_id')
        subscription_type = request.data.get('subscription_type')
        
        try:
            settings = OrganizationSettings.objects.get(organization_id=organization_id)
            settings.subscription_type = subscription_type
            settings.save()
            serializer = self.get_serializer(settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OrganizationSettings.DoesNotExist:
            return Response({'error': 'Organization settings not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class SuperadminOrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = SuperadminOrganizationSerializer
    permission_classes = [IsAuthenticated, IsSuperadmin]

    def perform_create(self, serializer):
        # Log organization creation
        org = serializer.save()
        SuperadminAuditLog.objects.create(
            superadmin=self.request.user,
            action='Created Organization',
            details={'organization_id': org.id, 'name': org.name}
        )

    def perform_destroy(self, instance):
        # Log organization deletion
        SuperadminAuditLog.objects.create(
            superadmin=self.request.user,
            action='Deleted Organization',
            details={'organization_id': instance.id, 'name': instance.name}
        )
        instance.delete()


class SuperadminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SuperadminUserSerializer
    permission_classes = [IsAuthenticated, IsSuperadmin]

    @action(detail=True, methods=['post'])
    def activate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        SuperadminAuditLog.objects.create(
            superadmin=request.user,
            action='Activated User',
            details={'user_id': user.id, 'email': user.email}
        )
        return Response({'status': 'user activated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deactivate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        SuperadminAuditLog.objects.create(
            superadmin=request.user,
            action='Deactivated User',
            details={'user_id': user.id, 'email': user.email}
        )
        return Response({'status': 'user deactivated'}, status=status.HTTP_200_OK)


class SubscriptionTypeViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionType.objects.all()
    serializer_class = SubscriptionTypeSerializer
    permission_classes = [IsAuthenticated, IsSuperadmin]

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        subscription = self.get_object()
        subscription.is_active = not subscription.is_active
        subscription.save()
        SuperadminAuditLog.objects.create(
            superadmin=request.user,
            action='Toggled Subscription Type',
            details={'subscription_id': subscription.id, 'name': subscription.name, 'is_active': subscription.is_active}
        )
        return Response(self.get_serializer(subscription).data, status=status.HTTP_200_OK)
