from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'cuisine_type', 'rating', 'phone', 'is_active')
    list_filter = ('is_active', 'cuisine_type')
    search_fields = ('name', 'address', 'owner__username')
