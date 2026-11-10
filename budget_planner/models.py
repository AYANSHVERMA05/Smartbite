from django.db import models
from django.conf import settings
from decimal import Decimal


class MealBudget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='meal_budgets'
    )
    daily_budget = models.DecimalField(max_digits=8, decimal_places=2)
    diet_preference = models.CharField(max_length=20, default='ALL')
    calculated_total = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    breakfast_item = models.ForeignKey(
        'menu.FoodItem', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='budget_breakfasts'
    )
    lunch_item = models.ForeignKey(
        'menu.FoodItem', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='budget_lunches'
    )
    dinner_item = models.ForeignKey(
        'menu.FoodItem', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='budget_dinners'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Budget Plan for {self.user.username} - ₹{self.daily_budget} ({self.created_at.strftime('%d %b %Y')})"

    @property
    def remaining_budget(self):
        return max(Decimal('0.00'), self.daily_budget - self.calculated_total)
