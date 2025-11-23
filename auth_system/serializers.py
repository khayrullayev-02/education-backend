from rest_framework import serializers
from core.models import CustomUser, Organization, Branch
from django.contrib.auth import authenticate

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'address', 'phone', 'email', 'logo', 'status', 'tariff', 'created_at']

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'organization', 'name', 'address', 'phone', 'status', 'created_at']

class CustomUserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'organization', 'branch', 'phone', 'date_of_birth', 'profile_image',
                  'is_blocked', 'two_factor_enabled', 'created_at']
        read_only_fields = ['created_at', 'is_blocked']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
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
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
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
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        return attrs
