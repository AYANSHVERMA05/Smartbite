from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SurplusFood, SurplusBooking
from restaurants.models import Restaurant
from menu.models import FoodCategory
from accounts.decorators import customer_required, restaurant_owner_required
from decimal import Decimal
import datetime


def surplus_list(request):
    now = timezone.now()
    # Auto-filter unexpired active listings with quantity > 0
    listings = SurplusFood.objects.filter(
        is_active=True,
        pickup_deadline__gt=now,
        available_quantity__gt=0
    ).select_related('restaurant', 'category')

    veg_only = request.GET.get('veg') == '1'
    if veg_only:
        listings = listings.filter(is_veg=True)

    return render(request, 'surplus_food/surplus_list.html', {
        'listings': listings,
        'veg_only': veg_only,
        'now': now,
    })


@login_required
@customer_required
def book_surplus(request, pk):
    now = timezone.now()
    item = get_object_or_404(SurplusFood, pk=pk, is_active=True, pickup_deadline__gt=now)

    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            qty = 1

        if qty > item.available_quantity:
            messages.error(request, f"Sorry, only {item.available_quantity} portions available.")
            return redirect('surplus_food:surplus_list')

        total = item.discounted_price * qty

        booking = SurplusBooking.objects.create(
            surplus_food=item,
            customer=request.user,
            quantity=qty,
            total_price=total,
            status='CONFIRMED'
        )

        item.available_quantity -= qty
        if item.available_quantity == 0:
            item.is_active = False
        item.save()

        messages.success(request, f"Surplus food reserved! Your Pickup Code is: {booking.booking_code}")
        return redirect('surplus_food:my_bookings')

    return render(request, 'surplus_food/book_surplus.html', {'item': item})


@login_required
@customer_required
def my_bookings(request):
    bookings = SurplusBooking.objects.filter(customer=request.user).select_related('surplus_food', 'surplus_food__restaurant')
    return render(request, 'surplus_food/my_bookings.html', {'bookings': bookings})


@login_required
@restaurant_owner_required
def owner_surplus_manage(request):
    restaurant = request.user.restaurant
    listings = restaurant.surplus_listings.all().order_by('-created_at')
    categories = FoodCategory.objects.all()

    if request.method == 'POST':
        food_name = request.POST.get('food_name', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        orig_price = Decimal(request.POST.get('original_price', '150'))
        disc_price = Decimal(request.POST.get('discounted_price', '75'))
        quantity = int(request.POST.get('quantity', 5))
        hours = int(request.POST.get('pickup_hours', 3))
        is_veg = request.POST.get('is_veg') == '1'
        image_url = request.POST.get('image_url', '').strip()

        deadline = timezone.now() + datetime.timedelta(hours=hours)

        SurplusFood.objects.create(
            restaurant=restaurant,
            food_name=food_name,
            category_id=category_id if category_id else None,
            description=description,
            original_price=orig_price,
            discounted_price=disc_price,
            available_quantity=quantity,
            pickup_deadline=deadline,
            is_veg=is_veg,
            image_url=image_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600"
        )

        messages.success(request, f"Surplus listing '{food_name}' posted successfully! Helps eliminate food waste.")
        return redirect('surplus_food:owner_surplus_manage')

    # Also fetch bookings for this restaurant's surplus food
    bookings = SurplusBooking.objects.filter(surplus_food__restaurant=restaurant).select_related('surplus_food', 'customer')

    return render(request, 'surplus_food/owner_surplus.html', {
        'restaurant': restaurant,
        'listings': listings,
        'categories': categories,
        'bookings': bookings,
    })


@login_required
@restaurant_owner_required
def owner_mark_pickup(request, booking_id):
    restaurant = request.user.restaurant
    booking = get_object_or_404(SurplusBooking, pk=booking_id, surplus_food__restaurant=restaurant)
    booking.status = 'PICKED_UP'
    booking.save()
    messages.success(request, f"Pickup verified for Booking #{booking.booking_code}!")
    return redirect('surplus_food:owner_surplus_manage')
