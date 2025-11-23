from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperadmin
from .models import SuperadminAuditLog, OrganizationSettings
from .serializers import SuperadminAuditLogSerializer, OrganizationSettingsSerializer


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
