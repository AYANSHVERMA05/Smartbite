from django.db import models


class FoodNutrition(models.Model):
    food_item = models.OneToOneField(
        'menu.FoodItem', 
        on_delete=models.CASCADE, 
        related_name='nutrition'
    )
    calories = models.PositiveIntegerField(help_text="Calories in kcal")
    protein = models.DecimalField(max_digits=5, decimal_places=1, help_text="Protein in grams")
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=1, help_text="Carbs in grams")
    fat = models.DecimalField(max_digits=5, decimal_places=1, help_text="Fat in grams")
    fiber = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, help_text="Fiber in grams")
    dietary_tags = models.CharField(
        max_length=200, 
        blank=True, 
        default='', 
        help_text="Comma-separated tags e.g. High Protein, Low Calorie, Healthy Choice"
    )

    def __str__(self):
        return f"Nutrition for {self.food_item.name} ({self.calories} kcal, {self.protein}g P)"

    @property
    def tag_list(self):
        if not self.dietary_tags:
            return []
        return [tag.strip() for tag in self.dietary_tags.split(',') if tag.strip()]
