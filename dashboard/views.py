from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from accounts.decorators import admin_required, restaurant_owner_required, customer_required
from orders.models import Order, OrderItem
from restaurants.models import Restaurant
from menu.models import FoodItem, FoodCategory
from surplus_food.models import SurplusFood, SurplusBooking
from subscriptions.models import Subscription, SubscriptionPlan
from budget_planner.models import MealBudget
import json

User = get_user_model()


@login_required
@customer_required
def customer_dashboard(request):
    user = request.user
    recent_orders = Order.objects.filter(user=user).select_related('restaurant')[:5]
    active_subscriptions = Subscription.objects.filter(user=user, status='ACTIVE').select_related('plan', 'plan__restaurant')
    surplus_bookings = SurplusBooking.objects.filter(customer=user).select_related('surplus_food')[:5]
    budget_history = MealBudget.objects.filter(user=user)[:3]

    total_spent = Order.objects.filter(user=user, payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'dashboard/customer_dashboard.html', {
        'recent_orders': recent_orders,
        'active_subscriptions': active_subscriptions,
        'surplus_bookings': surplus_bookings,
        'budget_history': budget_history,
        'total_spent': total_spent,
    })


@login_required
@restaurant_owner_required
def owner_dashboard(request):
    try:
        restaurant = request.user.restaurant
    except Restaurant.DoesNotExist:
        messages.error(request, "No restaurant registered under your account.")
        return redirect('menu:home')

    orders = Order.objects.filter(restaurant=restaurant).select_related('user').prefetch_related('items')
    total_orders = orders.count()
    total_revenue = orders.filter(payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0
    pending_orders = orders.filter(order_status='PENDING').count()
    preparing_orders = orders.filter(order_status='PREPARING').count()

    food_items = restaurant.food_items.all().select_related('category', 'nutrition')
    surplus_listings = restaurant.surplus_listings.all()

    return render(request, 'dashboard/owner_dashboard.html', {
        'restaurant': restaurant,
        'orders': orders[:15],
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'food_items': food_items,
        'surplus_listings': surplus_listings,
    })


@login_required
@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_customers = User.objects.filter(role='CUSTOMER').count()
    total_restaurants = Restaurant.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0
    active_subscriptions_count = Subscription.objects.filter(status='ACTIVE').count()
    surplus_saved_count = SurplusBooking.objects.filter(status='PICKED_UP').aggregate(qty=Sum('quantity'))['qty'] or 0

    # Chart 1: Order Status Breakdown (Doughnut)
    status_counts = list(Order.objects.values('order_status').annotate(count=Count('id')))
    status_labels = [dict(Order.STATUS_CHOICES).get(item['order_status'], item['order_status']) for item in status_counts]
    status_values = [item['count'] for item in status_counts]

    # Chart 2: Category Popularity (Bar)
    category_data = list(FoodCategory.objects.annotate(item_count=Count('food_items')).values('name', 'item_count'))
    cat_labels = [c['name'] for c in category_data]
    cat_values = [c['item_count'] for c in category_data]

    # Chart 3: Weekly Revenue Trend (Sample monthly trend)
    revenue_labels = ['Week 1', 'Week 2', 'Week 3', 'Current Week']
    revenue_values = [
        float(total_revenue) * 0.15,
        float(total_revenue) * 0.25,
        float(total_revenue) * 0.35,
        float(total_revenue) * 0.25,
    ] if total_revenue > 0 else [1200, 2400, 3100, 4500]

    recent_orders = Order.objects.select_related('user', 'restaurant')[:10]
    all_restaurants = Restaurant.objects.all().select_related('owner')
    all_customers = User.objects.filter(role='CUSTOMER')[:10]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_users': total_users,
        'total_customers': total_customers,
        'total_restaurants': total_restaurants,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'active_subscriptions_count': active_subscriptions_count,
        'surplus_saved_count': surplus_saved_count,
        'recent_orders': recent_orders,
        'all_restaurants': all_restaurants,
        'all_customers': all_customers,
        # JSON strings for Chart.js
        'status_labels_json': json.dumps(status_labels),
        'status_values_json': json.dumps(status_values),
        'cat_labels_json': json.dumps(cat_labels),
        'cat_values_json': json.dumps(cat_values),
        'revenue_labels_json': json.dumps(revenue_labels),
        'revenue_values_json': json.dumps(revenue_values),
    })


@login_required
@admin_required
def toggle_restaurant_status(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    restaurant.is_active = not restaurant.is_active
    restaurant.save()
    status_str = "Approved & Active" if restaurant.is_active else "Deactivated"
    messages.info(request, f"Restaurant '{restaurant.name}' is now {status_str}.")
    return redirect('dashboard:admin_dashboard')
