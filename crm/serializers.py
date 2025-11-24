from rest_framework import serializers
from core.models import Group, Course, Subject, Room, Teacher, RoomSchedule  # Import RoomSchedule model


class CourseSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'organization', 'organization_name', 'name', 'description', 'duration_hours', 'price', 'status', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'organization', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoomSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        # import lazily to avoid circular import at module import time
        model = __import__('core').models.Room
        fields = ['id', 'organization', 'branch', 'branch_name', 'name', 'capacity', 'location', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoomScheduleSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = RoomSchedule
        fields = ['id', 'room', 'room_name', 'group', 'group_name', 'days', 'start_time', 'end_time', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        # Ensure no duplicate schedules for the same room, days, and time
        overlapping_schedules = RoomSchedule.objects.filter(
            room=data['room'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            days__overlap=data['days']  # Check for overlapping days
        )
        if self.instance:
            overlapping_schedules = overlapping_schedules.exclude(id=self.instance.id)
        if overlapping_schedules.exists():
            raise serializers.ValidationError("Overlapping schedule exists for the selected room and time.")
        return data


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'user_full_name']  # Adjust fields as needed


# update GroupSerializer to use Subject relation
class GroupSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    teachers = TeacherSerializer(source='teacher_set', many=True, read_only=True)  # List of all teachers
    student_count = serializers.SerializerMethodField()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), allow_null=True, required=False)
    course_detail = CourseSerializer(source='course', read_only=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), allow_null=True, required=False)
    subject_detail = SubjectSerializer(source='subject', read_only=True)
    # room will be populated with Room FK; import lazily to avoid circular imports
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),  # Provide queryset for the Room model
        allow_null=True,
        required=False
    )
    room_detail = serializers.SerializerMethodField()
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),  # Provide queryset for the Teacher model
        allow_null=True,
        required=False
    )

    class Meta:
        model = Group
        fields = [
            'id', 'branch', 'branch_name',
            'name', 'subject', 'subject_detail', 'course', 'course_detail', 'teacher', 'teacher_name', 'teachers', 'room', 'room_detail',
            'level', 'max_students', 'student_count', 'students', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'student_count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_student_count(self, obj):
        return obj.students.count()

    def get_room_detail(self, obj):
        if obj.room:
            return {'id': str(obj.room.id), 'name': obj.room.name, 'capacity': obj.room.capacity, 'location': obj.room.location}
        return None

