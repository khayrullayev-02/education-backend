from django.contrib import admin
from .models import LoyaltyBranch, LoyaltyPoint


@admin.register(LoyaltyBranch)
class LoyaltyBranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'organization', 'status', 'points_multiplier', 'created_at')
    list_filter = ('status', 'organization', 'created_at')
    search_fields = ('name', 'branch__name', 'organization__name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(LoyaltyPoint)
class LoyaltyPointAdmin(admin.ModelAdmin):
    list_display = ('user', 'loyalty_branch', 'total_points', 'points_earned', 'points_redeemed', 'last_activity')
    list_filter = ('loyalty_branch', 'created_at', 'last_activity')
    search_fields = ('user__username', 'user__email', 'loyalty_branch__name')
    readonly_fields = ('id', 'created_at', 'last_activity')
