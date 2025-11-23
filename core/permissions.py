from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()


class IsSuperadmin(BasePermission):
    """
    Permission to check if user is a superadmin.
    """
    message = "Only superadmin users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'superadmin')


class IsDirector(BasePermission):
    """
    Permission to check if user is a director.
    """
    message = "Only director users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'director')


class IsManager(BasePermission):
    """
    Permission to check if user is a manager.
    """
    message = "Only manager users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'manager')


class IsAdmin(BasePermission):
    """
    Permission to check if user is an admin.
    """
    message = "Only admin users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsTeacher(BasePermission):
    """
    Permission to check if user is a teacher.
    """
    message = "Only teacher users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'teacher')


class IsStudent(BasePermission):
    """
    Permission to check if user is a student.
    """
    message = "Only student users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')


class IsParent(BasePermission):
    """
    Permission to check if user is a parent.
    """
    message = "Only parent users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'parent')


class IsStaff(BasePermission):
    """
    Permission to check if user is staff.
    """
    message = "Only staff users can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'staff')


class IsSameOrganization(BasePermission):
    """
    Permission to check if users belong to the same organization.
    """
    message = "Users must belong to the same organization."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(request.user.organization)


class IsSameBranch(BasePermission):
    """
    Permission to check if users belong to the same branch.
    """
    message = "Users must belong to the same branch."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(request.user.branch)


class HasBranchAccess(BasePermission):
    """
    Permission to check object-level access for branches.
    Only users in the same branch can access.
    """
    message = "You do not have access to this branch."
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'branch'):
            return obj.branch == request.user.branch
        elif hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        return False


class HasOrganizationAccess(BasePermission):
    """
    Permission to check object-level access for organizations.
    Only superadmin can access all organizations.
    Other roles can only access their own organization.
    """
    message = "You do not have access to this organization."
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'superadmin':
            return True
        return obj.organization == request.user.organization
