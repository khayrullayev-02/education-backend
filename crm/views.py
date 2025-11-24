from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers as drf_serializers
from core.models import Group, Course, Subject, Student, Room, RoomSchedule
from .serializers import GroupSerializer, CourseSerializer, SubjectSerializer
from rest_framework import serializers as drf_serializers
from .serializers import RoomSerializer, RoomScheduleSerializer



class GroupViewSet(viewsets.ModelViewSet):
    """
    Group Management
    
    Endpoints:
    - GET /api/groups/ - List all groups
    - POST /api/groups/ - Create new group
    - GET /api/groups/{id}/ - Retrieve group
    - PUT /api/groups/{id}/ - Update group
    - DELETE /api/groups/{id}/ - Delete group
    - POST /api/groups/{id}/activate/ - Activate group
    - POST /api/groups/{id}/deactivate/ - Deactivate group
    - GET /api/groups/{id}/statistics/ - Get group statistics
    """
    
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter groups by organization and branch"""
        user = self.request.user
        
        if not user or not user.is_authenticated:
            return Group.objects.all()
        
        if hasattr(user, 'role') and user.role == 'superadmin':
            return Group.objects.all()
        
        if hasattr(user, 'branch') and user.branch:
            return Group.objects.filter(branch=user.branch)
        
        if hasattr(user, 'organization') and user.organization:
            return Group.objects.filter(organization=user.organization)
        
        return Group.objects.all()

    def perform_create(self, serializer):
        # If authenticated and user has branch, assign it automatically
        if self.request.user.is_authenticated and hasattr(self.request.user, 'branch') and self.request.user.branch:
            serializer.save(branch=self.request.user.branch)
            return

        # If unauthenticated, require `branch` in request data
        branch_in_data = ('branch' in getattr(self.request, 'data', {}))
        if not branch_in_data:
            raise drf_serializers.ValidationError({'branch': 'This field is required when creating a group without authentication.'})

        serializer.save()

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """Add a student to the group (payload: {"student": "<student_uuid>"})"""
        group = self.get_object()
        student_id = request.data.get('student') or request.data.get('student_id')
        if not student_id:
            return Response({'detail': 'student is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'detail': 'student not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check branch compatibility
        if student.branch != group.branch:
            return Response({'detail': 'student branch does not match group branch'}, status=status.HTTP_400_BAD_REQUEST)

        # Check capacity
        if group.students.count() >= group.max_students:
            return Response({'detail': 'group is full'}, status=status.HTTP_400_BAD_REQUEST)

        group.students.add(student)
        group.save()
        serializer = self.get_serializer(group)
        return Response({'message': 'student added', 'data': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a group"""
        group = self.get_object()
        # If Group has a status field, toggle otherwise ignore
        if hasattr(group, 'status'):
            group.status = 'active'
            group.save()
        serializer = self.get_serializer(group)
        return Response({
            'message': 'Group activated',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a group"""
        group = self.get_object()
        if hasattr(group, 'status'):
            group.status = 'inactive'
            group.save()
        serializer = self.get_serializer(group)
        return Response({
            'message': 'Group deactivated',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a group"""
        group = self.get_object()
        # Compute student count from M2M field
        student_count = group.students.count()

        return Response({
            'group_id': group.id,
            'group_name': group.name,
            'teacher': group.teacher.user.full_name if group.teacher else 'N/A',
            'course': {
                'id': str(group.course.id) if group.course else None,
                'name': group.course.name if group.course else None,
                'duration_hours': group.course.duration_hours if group.course else None
            },
            'branch': group.branch.name,
            'level': group.level,
            'max_students': group.max_students,
            'current_students': student_count,
            'available_seats': group.max_students - student_count,
            'created_at': group.created_at,
        }, status=status.HTTP_200_OK)



class CourseViewSet(viewsets.ModelViewSet):
    """Simple Course API"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Course.objects.all()
        if hasattr(user, 'role') and user.role == 'superadmin':
            return Course.objects.all()
        if hasattr(user, 'organization') and user.organization:
            return Course.objects.filter(organization=user.organization)
        return Course.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization') and self.request.user.organization:
            serializer.save(organization=self.request.user.organization, created_by=self.request.user)
        else:
            serializer.save()


class SubjectViewSet(viewsets.ModelViewSet):
    """Simple Subject API"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Subject.objects.all()
        if hasattr(user, 'role') and user.role == 'superadmin':
            return Subject.objects.all()
        if hasattr(user, 'organization') and user.organization:
            return Subject.objects.filter(organization=user.organization)
        return Subject.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization') and self.request.user.organization:
            serializer.save(organization=self.request.user.organization)
        else:
            serializer.save()
    


class RoomViewSet(viewsets.ModelViewSet):
    """Room API: create rooms and list rooms. For scheduling use RoomSchedule endpoints."""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Room.objects.all()
        if hasattr(user, 'role') and user.role == 'superadmin':
            return Room.objects.all()
        if hasattr(user, 'organization') and user.organization:
            return Room.objects.filter(organization=user.organization)
        return Room.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organization') and self.request.user.organization:
            serializer.save(organization=self.request.user.organization)
        else:
            serializer.save()


class RoomScheduleViewSet(viewsets.ModelViewSet):
    """Room schedule API: assign room schedules to groups. Payload: {room: id, group: id, day: 'mon', start_time: '10:00', end_time: '11:30'}"""
    queryset = RoomSchedule.objects.all()
    serializer_class = RoomScheduleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return RoomSchedule.objects.none()
        return RoomSchedule.objects.all()

    def perform_create(self, serializer):
        # You may want to add validation for overlapping schedules here
        serializer.save()

