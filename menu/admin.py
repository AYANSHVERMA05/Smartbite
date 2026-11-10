from django.contrib import admin
from .models import FoodCategory, FoodItem, Review

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'meal_type', 'is_veg', 'is_available')
    list_filter = ('restaurant', 'category', 'meal_type', 'is_veg', 'is_available')
    search_fields = ('name', 'restaurant__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'food_item', 'rating', 'created_at')
    list_filter = ('rating',)
