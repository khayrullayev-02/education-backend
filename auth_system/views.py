# auth_system/views.py
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import CustomUser, Organization, Branch, Group
from .serializers import (
    CustomUserSerializer, UserCreateSerializer, LoginSerializer,
    ChangePasswordSerializer, OrganizationSerializer, BranchSerializer
)
from .permissions import IsSuperAdmin, IsDirector


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': CustomUserSerializer(user).data,
            'redirect': f'/{user.role}_dashboard',
        })


class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        return Response(
            CustomUserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if not user or not getattr(user, 'is_authenticated', False):
            return CustomUser.objects.none()

        if getattr(user, 'role', None) == 'superadmin':
            return CustomUser.objects.all()

        if getattr(user, 'organization', None):
            return CustomUser.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        user = serializer.save()
        if user.role == 'teacher':
            # Automatically assign teacher to groups if needed
            Group.objects.filter(branch=user.branch).update(teacher=user)

    def perform_update(self, serializer):
        user = serializer.save()
        if user.role == 'teacher':
            # Update teacher assignment in groups if needed
            Group.objects.filter(branch=user.branch).update(teacher=user)


class BranchViewSet(viewsets.ModelViewSet):
    """
    Branch Management ViewSet
    
    Endpoints:
    - GET /api/branches/ - List all branches
    - POST /api/branches/ - Create new branch
    - GET /api/branches/{id}/ - Retrieve branch
    - PUT /api/branches/{id}/ - Update branch
    - DELETE /api/branches/{id}/ - Delete branch
    """
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter branches by user organization"""
        user = self.request.user
        
        if not user or not user.is_authenticated:
            return Branch.objects.all()  # Return all branches for unauthenticated users during testing
        
        # Superadmin can see all branches
        if hasattr(user, 'role') and user.role == 'superadmin':
            return Branch.objects.all()
        
        # Other users see only their organization's branches
        if hasattr(user, 'organization') and user.organization:
            return Branch.objects.filter(organization=user.organization)
        
        return Branch.objects.none()
    
    def perform_create(self, serializer):
        """Set organization on creation - only if user is authenticated"""
        # For testing/frontend: allow creation without organization if not authenticated
        # In production, add IsAuthenticated permission
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization'):
            serializer.save(organization=self.request.user.organization)
        else:
            # During testing, allow saving without automatic organization assignment
            serializer.save()

