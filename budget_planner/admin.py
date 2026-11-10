from django.contrib import admin
from .models import MealBudget

@admin.register(MealBudget)
class MealBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_budget', 'diet_preference', 'calculated_total', 'created_at')
    list_filter = ('diet_preference', 'created_at')
