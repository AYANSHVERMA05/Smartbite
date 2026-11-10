from django.contrib import admin
from .models import SubscriptionPlan, Subscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'duration_type', 'meal_coverage', 'price', 'is_active')
    list_filter = ('duration_type', 'meal_coverage', 'is_active')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'delivery_hostel_address')
