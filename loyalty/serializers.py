from rest_framework import serializers
from .models import LoyaltyBranch, LoyaltyPoint


class LoyaltyBranchSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = LoyaltyBranch
        fields = [
            'id', 'branch', 'branch_name', 'organization', 'organization_name', 
            'name', 'description', 'points_multiplier', 'min_purchase_for_points',
            'status', 'is_primary', 'created_by', 'created_by_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class LoyaltyPointSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    loyalty_branch_name = serializers.CharField(source='loyalty_branch.name', read_only=True)
    
    class Meta:
        model = LoyaltyPoint
        fields = [
            'id', 'loyalty_branch', 'loyalty_branch_name', 'user', 'user_name',
            'points_earned', 'points_redeemed', 'total_points', 'last_activity', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity', 'total_points']
