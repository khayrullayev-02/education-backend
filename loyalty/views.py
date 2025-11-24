from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from core.models import Branch
from .models import LoyaltyBranch, LoyaltyPoint
from .serializers import LoyaltyBranchSerializer, LoyaltyPointSerializer


class LoyaltyBranchViewSet(viewsets.ModelViewSet):
    """
    Loyalty Program Branch Management
    
    Endpoints:
    - GET /api/loyalty/branches/ - List all loyalty branches
    - POST /api/loyalty/branches/ - Create new loyalty branch
    - GET /api/loyalty/branches/{id}/ - Retrieve loyalty branch details
    - PUT /api/loyalty/branches/{id}/ - Update loyalty branch
    - DELETE /api/loyalty/branches/{id}/ - Delete loyalty branch
    - POST /api/loyalty/branches/{id}/toggle_status/ - Activate/Deactivate branch
    - GET /api/loyalty/branches/{id}/statistics/ - Get branch statistics
    """
    
    queryset = LoyaltyBranch.objects.all()
    serializer_class = LoyaltyBranchSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter loyalty branches by organization"""
        user = self.request.user
        
        # Check if user is authenticated
        if not user or not user.is_authenticated:
            return LoyaltyBranch.objects.all()  # Return all during testing
        
        # Superadmin can see all branches
        if hasattr(user, 'role') and user.role == 'superadmin':
            return LoyaltyBranch.objects.all()
        
        # Other users see only their organization's branches
        if hasattr(user, 'organization') and user.organization:
            return LoyaltyBranch.objects.filter(organization=user.organization)
        
        return LoyaltyBranch.objects.all()
    
    def perform_create(self, serializer):
        """Set organization and created_by on creation - only if authenticated"""
        if self.request.user.is_authenticated:
            serializer.save(
                organization=self.request.user.organization,
                created_by=self.request.user
            )
        else:
            # During testing: allow creation without these fields if not authenticated
            # Note: organization field will need to be provided in request data
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def available_branches(self, request):
        """Get list of available branches for creating loyalty branches"""
        user = self.request.user
        
        # Get branches based on user role - allow all branches during testing
        if hasattr(user, 'role') and user.role == 'superadmin':
            branches = Branch.objects.all()
        elif hasattr(user, 'organization') and user.organization:
            branches = Branch.objects.filter(organization=user.organization)
        else:
            # During testing: return all branches
            branches = Branch.objects.all()
        
        branch_list = [
            {
                'id': str(branch.id),
                'name': branch.name,
                'organization': branch.organization.name,
                'address': branch.address,
                'phone': branch.phone,
                'status': branch.status
            }
            for branch in branches
        ]
        
        return Response({
            'total': len(branch_list),
            'branches': branch_list
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle loyalty branch status between active and inactive"""
        loyalty_branch = self.get_object()
        
        if loyalty_branch.status == 'active':
            loyalty_branch.status = 'inactive'
        else:
            loyalty_branch.status = 'active'
        
        loyalty_branch.save()
        serializer = self.get_serializer(loyalty_branch)
        return Response({
            'message': f'Loyalty branch status changed to {loyalty_branch.status}',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a loyalty branch"""
        loyalty_branch = self.get_object()
        
        total_points = LoyaltyPoint.objects.filter(
            loyalty_branch=loyalty_branch
        ).aggregate(
            total=Sum('total_points'),
            earned=Sum('points_earned'),
            redeemed=Sum('points_redeemed')
        )
        
        member_count = LoyaltyPoint.objects.filter(
            loyalty_branch=loyalty_branch
        ).count()
        
        return Response({
            'branch_id': loyalty_branch.id,
            'branch_name': loyalty_branch.name,
            'total_members': member_count,
            'total_points_in_circulation': total_points['total'] or 0,
            'total_points_earned': total_points['earned'] or 0,
            'total_points_redeemed': total_points['redeemed'] or 0,
            'average_points_per_member': (total_points['total'] or 0) / (member_count or 1)
        }, status=status.HTTP_200_OK)


class LoyaltyPointViewSet(viewsets.ModelViewSet):
    """
    Loyalty Points Management
    
    Endpoints:
    - GET /api/loyalty/points/ - List all loyalty points
    - POST /api/loyalty/points/ - Create loyalty points record
    - GET /api/loyalty/points/{id}/ - Retrieve loyalty points
    - PUT /api/loyalty/points/{id}/ - Update loyalty points
    - POST /api/loyalty/points/{id}/add_points/ - Add points to user
    - POST /api/loyalty/points/{id}/redeem_points/ - Redeem user points
    """
    
    queryset = LoyaltyPoint.objects.all()
    serializer_class = LoyaltyPointSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter loyalty points by user organization"""
        user = self.request.user
        
        # Check if user is authenticated
        if not user or not user.is_authenticated:
            return LoyaltyPoint.objects.all()  # Return all during testing
        
        # Superadmin can see all points
        if hasattr(user, 'role') and user.role == 'superadmin':
            return LoyaltyPoint.objects.all()
        
        # Other users see only their organization's points
        if hasattr(user, 'organization') and user.organization:
            return LoyaltyPoint.objects.filter(
                loyalty_branch__organization=user.organization
            )
        
        return LoyaltyPoint.objects.all()
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """Add loyalty points to a user"""
        loyalty_point = self.get_object()
        points = request.data.get('points', 0)
        
        try:
            points = float(points)
            if points <= 0:
                return Response(
                    {'error': 'Points must be greater than 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            loyalty_point.points_earned += points
            loyalty_point.total_points += points
            loyalty_point.save()
            
            serializer = self.get_serializer(loyalty_point)
            return Response({
                'message': f'{points} points added successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid points value'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def redeem_points(self, request, pk=None):
        """Redeem loyalty points from a user"""
        loyalty_point = self.get_object()
        points = request.data.get('points', 0)
        
        try:
            points = float(points)
            if points <= 0:
                return Response(
                    {'error': 'Points must be greater than 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if loyalty_point.total_points < points:
                return Response(
                    {'error': f'Insufficient points. Available: {loyalty_point.total_points}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            loyalty_point.points_redeemed += points
            loyalty_point.total_points -= points
            loyalty_point.save()
            
            serializer = self.get_serializer(loyalty_point)
            return Response({
                'message': f'{points} points redeemed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid points value'},
                status=status.HTTP_400_BAD_REQUEST
            )
