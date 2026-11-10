from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import FoodItem, FoodCategory, Review
from .forms import FoodItemForm, ReviewForm
from nutrition.models import FoodNutrition
from restaurants.models import Restaurant
from surplus_food.models import SurplusFood
from accounts.decorators import restaurant_owner_required
from django.utils import timezone


def home(request):
    featured_categories = FoodCategory.objects.all()[:6]
    popular_foods = FoodItem.objects.filter(is_available=True).select_related('restaurant', 'category', 'nutrition')[:8]
    featured_restaurants = Restaurant.objects.filter(is_active=True)[:4]
    active_surplus = SurplusFood.objects.filter(is_active=True, available_quantity__gt=0, pickup_deadline__gt=timezone.now())[:4]

    return render(request, 'menu/home.html', {
        'featured_categories': featured_categories,
        'popular_foods': popular_foods,
        'featured_restaurants': featured_restaurants,
        'active_surplus': active_surplus,
    })


def food_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    meal_type = request.GET.get('meal_type', '').strip()
    is_veg = request.GET.get('is_veg', '').strip()
    sort = request.GET.get('sort', '').strip()

    items = FoodItem.objects.filter(is_available=True).select_related('restaurant', 'category', 'nutrition')

    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(restaurant__name__icontains=query)
        )

    if category_id:
        items = items.filter(category_id=category_id)

    if meal_type:
        items = items.filter(meal_type=meal_type)

    if is_veg == '1':
        items = items.filter(is_veg=True)
    elif is_veg == '0':
        items = items.filter(is_veg=False)

    if sort == 'price_asc':
        items = items.order_by('price')
    elif sort == 'price_desc':
        items = items.order_by('-price')
    elif sort == 'name':
        items = items.order_by('name')

    categories = FoodCategory.objects.all()

    return render(request, 'menu/food_list.html', {
        'food_items': items,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_meal': meal_type,
        'selected_veg': is_veg,
        'selected_sort': sort,
    })


def food_detail(request, pk):
    item = get_object_or_404(FoodItem.objects.select_related('restaurant', 'category', 'nutrition'), pk=pk)
    reviews = item.reviews.all().select_related('user')[:10]
    review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.food_item = item
            review.user = request.user
            review.restaurant = item.restaurant
            review.save()
            messages.success(request, "Thank you! Your review has been posted.")
            return redirect('menu:food_detail', pk=item.pk)

    # Similar dishes from same category
    similar_items = FoodItem.objects.filter(category=item.category, is_available=True).exclude(pk=item.pk)[:4]

    return render(request, 'menu/food_detail.html', {
        'item': item,
        'reviews': reviews,
        'review_form': review_form,
        'similar_items': similar_items,
    })


@login_required
@restaurant_owner_required
def add_food_item(request):
    try:
        restaurant = request.user.restaurant
    except Restaurant.DoesNotExist:
        messages.error(request, "No restaurant registered under your account.")
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        calories = request.POST.get('calories', '350')
        protein = request.POST.get('protein', '12.0')
        carbs = request.POST.get('carbohydrates', '45.0')
        fat = request.POST.get('fat', '10.0')

        if form.is_valid():
            food = form.save(commit=False)
            food.restaurant = restaurant
            food.save()

            # Create default nutrition record
            try:
                FoodNutrition.objects.create(
                    food_item=food,
                    calories=int(calories) if calories else 350,
                    protein=float(protein) if protein else 12.0,
                    carbohydrates=float(carbs) if carbs else 45.0,
                    fat=float(fat) if fat else 10.0,
                    dietary_tags="High Protein" if float(protein or 0) >= 15 else "Campus Choice"
                )
            except Exception:
                pass

            messages.success(request, f"'{food.name}' added successfully to your menu!")
            return redirect('dashboard:owner_dashboard')
    else:
        form = FoodItemForm()

    return render(request, 'menu/food_form.html', {
        'form': form,
        'title': 'Add New Food Item',
        'is_edit': False
    })


@login_required
@restaurant_owner_required
def edit_food_item(request, pk):
    restaurant = request.user.restaurant
    food = get_object_or_404(FoodItem, pk=pk, restaurant=restaurant)
    nutrition = getattr(food, 'nutrition', None)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, instance=food)
        calories = request.POST.get('calories')
        protein = request.POST.get('protein')
        carbs = request.POST.get('carbohydrates')
        fat = request.POST.get('fat')

        if form.is_valid():
            form.save()
            if nutrition and calories and protein:
                nutrition.calories = int(calories)
                nutrition.protein = float(protein)
                nutrition.carbohydrates = float(carbs)
                nutrition.fat = float(fat)
                nutrition.save()

            messages.success(request, f"'{food.name}' updated successfully.")
            return redirect('dashboard:owner_dashboard')
    else:
        form = FoodItemForm(instance=food)

    return render(request, 'menu/food_form.html', {
        'form': form,
        'title': f'Edit {food.name}',
        'food': food,
        'nutrition': nutrition,
        'is_edit': True
    })


@login_required
@restaurant_owner_required
def delete_food_item(request, pk):
    restaurant = request.user.restaurant
    food = get_object_or_404(FoodItem, pk=pk, restaurant=restaurant)

    if request.method == 'POST':
        name = food.name
        food.delete()
        messages.success(request, f"'{name}' deleted from your menu.")
        return redirect('dashboard:owner_dashboard')

    return render(request, 'menu/food_confirm_delete.html', {'food': food})


@login_required
@restaurant_owner_required
def toggle_food_availability(request, pk):
    restaurant = request.user.restaurant
    food = get_object_or_404(FoodItem, pk=pk, restaurant=restaurant)
    food.is_available = not food.is_available
    food.save()
    status_str = "Available" if food.is_available else "Unavailable"
    messages.info(request, f"'{food.name}' status toggled to {status_str}.")
    return redirect('dashboard:owner_dashboard')
