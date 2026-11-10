from django.db import models
from django.conf import settings
from decimal import Decimal


class UserFoodPreference(models.Model):
    CALORIE_CHOICES = (
        ('ANY', 'No Preference'),
        ('LOW', 'Low Calorie (< 400 kcal)'),
        ('HIGH_PROTEIN', 'High Protein (> 20g)'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='food_preference'
    )
    is_vegetarian = models.BooleanField(default=False)
    preferred_categories = models.ManyToManyField('menu.FoodCategory', blank=True)
    max_budget_per_item = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('300.00'))
    calorie_preference = models.CharField(max_length=20, choices=CALORIE_CHOICES, default='ANY')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences of {self.user.username}"
