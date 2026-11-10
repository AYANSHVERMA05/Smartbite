from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.item_total() for item in self.items.all())

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey('menu.FoodItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def item_total(self):
        return self.food_item.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Order Placed (Pending)'),
        ('PREPARING', 'Kitchen Preparing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
    )
    order_number = models.CharField(max_length=24, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=9, decimal_places=2)
    delivery_address = models.TextField()
    contact_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, default='UNPAID')
    order_status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    special_instructions = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SB-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} by {self.user.username} (₹{self.total_amount})"

    @property
    def status_badge_class(self):
        mapping = {
            'PENDING': 'bg-warning text-dark',
            'PREPARING': 'bg-info text-dark',
            'OUT_FOR_DELIVERY': 'bg-primary text-white',
            'DELIVERED': 'bg-success text-white',
            'CANCELLED': 'bg-danger text-white',
        }
        return mapping.get(self.order_status, 'bg-secondary')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(
        'menu.FoodItem', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    food_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def item_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.food_name}"
