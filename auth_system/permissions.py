from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'superadmin'

class IsDirector(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['superadmin', 'director']

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['superadmin', 'director', 'manager']

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['superadmin', 'director', 'manager', 'admin']

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['teacher']

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['student']

class IsInSameOrganization(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'superadmin':
            return True
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        if hasattr(obj, 'branch') and hasattr(obj.branch, 'organization'):
            return obj.branch.organization == request.user.organization
        return False
