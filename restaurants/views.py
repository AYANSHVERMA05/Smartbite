from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Restaurant
from .forms import RestaurantProfileForm
from accounts.decorators import restaurant_owner_required
from menu.models import FoodItem, FoodCategory


def restaurant_list(request):
    query = request.GET.get('q', '').strip()
    cuisine = request.GET.get('cuisine', '').strip()

    restaurants = Restaurant.objects.filter(is_active=True)

    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) | 
            Q(cuisine_type__icontains=query) | 
            Q(description__icontains=query)
        )

    if cuisine:
        restaurants = restaurants.filter(cuisine_type__icontains=cuisine)

    cuisines = Restaurant.objects.values_list('cuisine_type', flat=True).distinct()

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants,
        'query': query,
        'selected_cuisine': cuisine,
        'cuisines': cuisines,
    })


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    categories = FoodCategory.objects.filter(food_items__restaurant=restaurant).distinct()
    food_items = restaurant.food_items.filter(is_available=True).select_related('nutrition', 'category')
    
    # Filter by category if requested
    cat_id = request.GET.get('cat')
    if cat_id:
        food_items = food_items.filter(category_id=cat_id)

    # Filter veg
    veg_only = request.GET.get('veg') == '1'
    if veg_only:
        food_items = food_items.filter(is_veg=True)

    reviews = restaurant.reviews.all().select_related('user')[:10]

    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'categories': categories,
        'food_items': food_items,
        'selected_cat': cat_id,
        'veg_only': veg_only,
        'reviews': reviews,
    })


@login_required
@restaurant_owner_required
def owner_restaurant_profile(request):
    try:
        restaurant = request.user.restaurant
    except Restaurant.DoesNotExist:
        messages.error(request, "No restaurant registered under your account.")
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Restaurant details updated successfully!")
            return redirect('restaurants:owner_restaurant_profile')
    else:
        form = RestaurantProfileForm(instance=restaurant)

    return render(request, 'restaurants/owner_profile.html', {
        'form': form,
        'restaurant': restaurant
    })
