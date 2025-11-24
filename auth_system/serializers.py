from rest_framework import serializers
from core.models import CustomUser, Organization, Branch
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group

class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization management"""
    class Meta:
        model = Organization
        fields = ['id', 'name', 'address', 'phone', 'email', 'logo', 'status', 'tariff', 'created_at']

class BranchSerializer(serializers.ModelSerializer):
    """Serializer for Branch management"""
    class Meta:
        model = Branch
        fields = ['id', 'organization', 'name', 'address', 'phone', 'status', 'created_at']

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for User with related organization and branch"""
    organization = OrganizationSerializer(read_only=True, help_text="Organization details")
    branch = BranchSerializer(read_only=True, help_text="Branch details")
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False, help_text="Groups assigned to the user"
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'organization', 'branch', 'phone', 'date_of_birth', 'profile_image',
                  'is_blocked', 'two_factor_enabled', 'created_at', 'groups']
        read_only_fields = ['created_at', 'is_blocked']

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        user = super().create(validated_data)
        if groups:
            user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        instance = super().update(instance, validated_data)
        if groups is not None:
            instance.groups.set(groups)
        return instance

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8, help_text="Password (minimum 8 characters)")
    password_confirm = serializers.CharField(write_only=True, help_text="Confirm password")
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'role', 'organization', 'branch', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(help_text="Username or email")
    password = serializers.CharField(write_only=True, help_text="User password")
    
    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if user.is_blocked:
            raise serializers.ValidationError("User account is blocked")
        if user.organization and user.organization.status == 'frozen':
            raise serializers.ValidationError("Organization is frozen")
        attrs['user'] = user
        return attrs

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password"""
    old_password = serializers.CharField(write_only=True, help_text="Current password")
    new_password = serializers.CharField(write_only=True, min_length=8, help_text="New password (minimum 8 characters)")
    new_password_confirm = serializers.CharField(write_only=True, help_text="Confirm new password")
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        return attrs
