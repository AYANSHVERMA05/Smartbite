from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='restaurant'
    )
    name = models.CharField(max_length=150)
    description = models.TextField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    cuisine_type = models.CharField(max_length=100, default='Multi-Cuisine')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    opening_time = models.TimeField(default='08:00:00')
    closing_time = models.TimeField(default='22:00:00')
    image_url = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating', 'name']

    def __str__(self):
        return self.name

    @property
    def total_items(self):
        return self.food_items.count()
