from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    DURATION_CHOICES = (
        ('WEEKLY', 'Weekly (7 Days)'),
        ('MONTHLY', 'Monthly (30 Days)'),
    )
    MEAL_CHOICES = (
        ('BREAKFAST', 'Breakfast Only'),
        ('LUNCH_DINNER', 'Lunch & Dinner'),
        ('ALL_THREE', 'Breakfast, Lunch & Dinner'),
    )
    PLAN_TYPE_CHOICES = (
        ('VEG', 'Pure Vegetarian'),
        ('NON_VEG', 'Non-Veg Options Included'),
        ('COMBO', 'Special Student Mess Combo'),
    )

    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='subscription_plans'
    )
    name = models.CharField(max_length=120)
    duration_type = models.CharField(max_length=20, choices=DURATION_CHOICES, default='MONTHLY')
    meal_coverage = models.CharField(max_length=30, choices=MEAL_CHOICES, default='LUNCH_DINNER')
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='VEG')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    features = models.TextField(
        help_text="Separate features by newlines (e.g. Unlimited Rice/Rotis, Weekend Sweets)"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ₹{self.price} ({self.get_duration_type_display()})"

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.CASCADE, 
        related_name='user_subscriptions'
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    delivery_hostel_address = models.CharField(
        max_length=255, 
        help_text="e.g. Block C - Room 310, Tagore Hostel"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

    @property
    def is_currently_active(self):
        if self.status != 'ACTIVE':
            return False
        return self.end_date >= timezone.now().date()
