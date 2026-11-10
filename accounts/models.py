from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('RESTAURANT_OWNER', 'Restaurant Owner'),
        ('ADMIN', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=15, blank=True, null=True)

    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'

    @property
    def is_restaurant_owner(self):
        return self.role == 'RESTAURANT_OWNER'

    @property
    def is_admin_user(self):
        return self.role == 'ADMIN' or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class CustomerProfile(models.Model):
    DIET_CHOICES = (
        ('ALL', 'All Foods'),
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    delivery_address = models.TextField(blank=True, default='')
    hostel_block_room = models.CharField(max_length=100, blank=True, default='', help_text="e.g. Block B, Room 204")
    preferred_diet = models.CharField(max_length=20, choices=DIET_CHOICES, default='ALL')
    daily_budget_limit = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
