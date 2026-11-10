from django.contrib import admin
from .models import FoodNutrition

@admin.register(FoodNutrition)
class FoodNutritionAdmin(admin.ModelAdmin):
    list_display = ('food_item', 'calories', 'protein', 'carbohydrates', 'fat', 'dietary_tags')
    search_fields = ('food_item__name', 'dietary_tags')
