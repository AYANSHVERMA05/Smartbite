from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .planner_logic import generate_budget_meal_plans
from .models import MealBudget
from menu.models import FoodItem
from orders.models import Cart, CartItem


def budget_planner_view(request):
    initial_budget = "350"
    initial_diet = "ALL"

    if request.user.is_authenticated:
        profile = getattr(request.user, 'customer_profile', None)
        if profile and profile.daily_budget_limit:
            initial_budget = str(profile.daily_budget_limit)
            initial_diet = profile.preferred_diet

    budget_str = request.GET.get('budget', initial_budget).strip()
    diet = request.GET.get('diet', initial_diet).strip()

    try:
        budget = Decimal(budget_str)
        if budget < 50:
            budget = Decimal('50.00')
    except Exception:
        budget = Decimal('350.00')

    meal_plans = generate_budget_meal_plans(daily_budget=budget, diet_preference=diet, max_plans=3)

    # Affordable single items under budget
    items_under_budget = FoodItem.objects.filter(is_available=True, price__lte=budget).select_related('restaurant', 'nutrition')
    if diet == 'VEG':
        items_under_budget = items_under_budget.filter(is_veg=True)
    items_under_budget = items_under_budget.order_by('price')[:12]

    # Save to history if logged in
    if request.user.is_authenticated and meal_plans:
        top = meal_plans[0]
        MealBudget.objects.create(
            user=request.user,
            daily_budget=budget,
            diet_preference=diet,
            calculated_total=top['total_cost'],
            breakfast_item=top['breakfast'],
            lunch_item=top['lunch'],
            dinner_item=top['dinner']
        )

    return render(request, 'budget_planner/planner.html', {
        'budget': budget,
        'diet': diet,
        'meal_plans': meal_plans,
        'items_under_budget': items_under_budget,
    })


@login_required
def add_combo_to_cart(request):
    if request.method == 'POST':
        b_id = request.POST.get('breakfast_id')
        l_id = request.POST.get('lunch_id')
        d_id = request.POST.get('dinner_id')

        cart, _ = Cart.objects.get_or_create(user=request.user)

        items_added = 0
        for item_id in [b_id, l_id, d_id]:
            if item_id:
                try:
                    food = FoodItem.objects.get(pk=item_id, is_available=True)
                    ci, created = CartItem.objects.get_or_create(cart=cart, food_item=food)
                    if not created:
                        ci.quantity += 1
                        ci.save()
                    items_added += 1
                except FoodItem.DoesNotExist:
                    pass

        messages.success(request, f"Successfully added {items_added} items from your budget meal plan to the cart!")
        return redirect('orders:view_cart')

    return redirect('budget_planner:planner')
