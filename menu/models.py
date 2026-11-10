from django.db import models
from django.conf import settings


class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, default='fa-utensils')
    image_url = models.URLField(blank=True, default='')

    class Meta:
        verbose_name_plural = 'Food Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    MEAL_CHOICES = (
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('DINNER', 'Dinner'),
        ('SNACK', 'Snacks & Beverages'),
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='food_items'
    )
    category = models.ForeignKey(
        FoodCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='food_items'
    )
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, default='LUNCH')
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(default=20, help_text="Time in minutes")
    image_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ₹{self.price} ({self.restaurant.name})"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 4.5


class Review(models.Model):
    food_item = models.ForeignKey(
        FoodItem, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        null=True, 
        blank=True
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        null=True, 
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.food_item.name if self.food_item else self.restaurant.name
        return f"Review by {self.user.username} for {target} ({self.rating}/5)"
