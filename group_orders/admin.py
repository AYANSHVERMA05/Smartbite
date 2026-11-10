from django.contrib import admin
from .models import GroupOrder, GroupMember, GroupOrderItem

@admin.register(GroupOrder)
class GroupOrderAdmin(admin.ModelAdmin):
    list_display = ('group_code', 'title', 'host', 'restaurant', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('group_code', 'title', 'host__username')

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group_order', 'joined_at')

@admin.register(GroupOrderItem)
class GroupOrderItemAdmin(admin.ModelAdmin):
    list_display = ('group_order', 'member', 'food_item', 'quantity')
