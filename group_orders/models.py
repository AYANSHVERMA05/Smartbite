from django.db import models
from django.conf import settings
from decimal import Decimal
import secrets


def generate_group_code():
    return secrets.token_hex(3).upper()  # 6-character clean unique alphanumeric code


class GroupOrder(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open (Accepting Items)'),
        ('LOCKED', 'Locked (Finalizing Bill)'),
        ('PLACED', 'Placed as Order (COD)'),
        ('CANCELLED', 'Cancelled'),
    )
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='hosted_group_orders'
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='group_orders'
    )
    group_code = models.CharField(max_length=10, unique=True, default=generate_group_code)
    title = models.CharField(max_length=120, default='Hostel Friends Feast')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    delivery_address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Group Order [{self.group_code}] - {self.title} (Host: {self.host.username})"

    def total_bill(self):
        return sum(item.item_total() for item in self.order_items.all())

    def member_count(self):
        return self.members.count()


class GroupMember(models.Model):
    group_order = models.ForeignKey(GroupOrder, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='group_memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group_order', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.group_order.group_code}"

    def member_total(self):
        return sum(item.item_total() for item in self.items.all())


class GroupOrderItem(models.Model):
    group_order = models.ForeignKey(GroupOrder, on_delete=models.CASCADE, related_name='order_items')
    member = models.ForeignKey(GroupMember, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey('menu.FoodItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    special_notes = models.CharField(max_length=150, blank=True, default='')

    def item_total(self):
        return self.food_item.price * self.quantity

    def __str__(self):
        return f"{self.member.user.username}: {self.quantity}x {self.food_item.name}"
