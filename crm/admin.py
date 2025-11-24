from django.contrib import admin
from core.models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'course', 'teacher', 'max_students', 'created_at')
    list_filter = ('branch',)
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')

from core.models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'duration_hours', 'price', 'status', 'created_at')
    list_filter = ('status', 'organization')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')
