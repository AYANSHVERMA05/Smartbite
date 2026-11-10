from django.contrib import admin
from .models import UserFoodPreference

@admin.register(UserFoodPreference)
class UserFoodPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_vegetarian', 'max_budget_per_item', 'calorie_preference', 'updated_at')
