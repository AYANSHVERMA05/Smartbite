from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import secrets


def generate_booking_code():
    return f"SB-SP-{secrets.token_hex(2).upper()}"


class SurplusFood(models.Model):
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='surplus_listings'
    )
    food_name = models.CharField(max_length=150)
    category = models.ForeignKey(
        'menu.FoodCategory', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    description = models.TextField()
    original_price = models.DecimalField(max_digits=7, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=7, decimal_places=2)
    available_quantity = models.PositiveIntegerField(default=1)
    pickup_deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_veg = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pickup_deadline']

    def __str__(self):
        return f"{self.food_name} @ ₹{self.discounted_price} ({self.restaurant.name})"

    @property
    def is_expired(self):
        return timezone.now() > self.pickup_deadline

    @property
    def is_available_for_booking(self):
        return self.is_active and not self.is_expired and self.available_quantity > 0

    @property
    def discount_percent(self):
        if self.original_price > 0:
            pct = int(((self.original_price - self.discounted_price) / self.original_price) * 100)
            return max(0, pct)
        return 0


class SurplusBooking(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed (Awaiting Pickup)'),
        ('PICKED_UP', 'Picked Up'),
        ('CANCELLED', 'Cancelled'),
    )
    surplus_food = models.ForeignKey(
        SurplusFood, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='surplus_bookings'
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    booking_code = models.CharField(max_length=16, unique=True, default=generate_booking_code)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.booking_code} - {self.surplus_food.food_name} by {self.customer.username}"
