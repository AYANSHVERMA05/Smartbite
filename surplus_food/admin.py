from django.contrib import admin
from .models import SurplusFood, SurplusBooking

@admin.register(SurplusFood)
class SurplusFoodAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'restaurant', 'discounted_price', 'original_price', 'available_quantity', 'pickup_deadline', 'is_active')
    list_filter = ('is_active', 'is_veg', 'restaurant')

@admin.register(SurplusBooking)
class SurplusBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_code', 'customer', 'surplus_food', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking_code', 'customer__username')
