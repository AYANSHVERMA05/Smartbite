from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from menu.models import FoodItem
from accounts.decorators import customer_required, restaurant_owner_required
from decimal import Decimal


@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('food_item', 'food_item__restaurant').all()
    
    # Check if items are from different restaurants
    restaurants = set(item.food_item.restaurant for item in cart_items)
    is_multi_restaurant = len(restaurants) > 1

    return render(request, 'orders/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'is_multi_restaurant': is_multi_restaurant,
    })


@login_required
def add_to_cart(request, food_id):
    food_item = get_object_or_404(FoodItem, pk=food_id, is_available=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Updated quantity of '{food_item.name}' in your cart.")
    else:
        messages.success(request, f"Added '{food_item.name}' to your cart.")

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('orders:view_cart')


@login_required
def update_cart_item(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    action = request.POST.get('action')

    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
            return redirect('orders:view_cart')
    elif action == 'remove':
        cart_item.delete()
        messages.info(request, "Item removed from cart.")

    return redirect('orders:view_cart')


@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    cart_item.delete()
    messages.info(request, "Item removed from your cart.")
    return redirect('orders:view_cart')


@login_required
@customer_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('food_item', 'food_item__restaurant').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty! Add some delicious food first.")
        return redirect('menu:food_list')

    # Primary restaurant from first cart item
    primary_restaurant = cart_items.first().food_item.restaurant
    profile = getattr(request.user, 'customer_profile', None)
    default_address = profile.delivery_address if profile and profile.delivery_address else (profile.hostel_block_room if profile else '')

    if request.method == 'POST':
        address = request.POST.get('delivery_address', '').strip()
        phone = request.POST.get('contact_phone', '').strip()
        instructions = request.POST.get('special_instructions', '').strip()

        if not address or not phone:
            messages.error(request, "Delivery address and contact phone are required.")
            return redirect('orders:checkout')

        # Create Order
        total = cart.total_price()
        order = Order.objects.create(
            user=request.user,
            restaurant=primary_restaurant,
            total_amount=total,
            delivery_address=address,
            contact_phone=phone,
            payment_method='COD',
            payment_status='UNPAID',
            order_status='PENDING',
            special_instructions=instructions
        )

        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                food_item=ci.food_item,
                food_name=ci.food_item.name,
                price=ci.food_item.price,
                quantity=ci.quantity
            )

        # Clear cart
        cart_items.delete()

        messages.success(request, f"Order #{order.order_number} placed successfully! Please pay cash on delivery.")
        return redirect('orders:order_success', order_number=order.order_number)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'restaurant': primary_restaurant,
        'default_address': default_address,
        'phone': request.user.phone or '',
    })


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).select_related('restaurant').prefetch_related('items')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    # Allowed for customer who placed it, restaurant owner, or admin
    order = get_object_or_404(Order.objects.select_related('restaurant', 'user').prefetch_related('items'), order_number=order_number)

    is_allowed = (
        request.user == order.user or 
        (request.user.is_restaurant_owner and request.user.restaurant == order.restaurant) or
        request.user.is_admin_user
    )

    if not is_allowed:
        messages.error(request, "You do not have permission to view this order.")
        return redirect('accounts:dashboard_redirect')

    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
@restaurant_owner_required
def update_order_status(request, order_id):
    restaurant = request.user.restaurant
    order = get_object_or_404(Order, pk=order_id, restaurant=restaurant)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.order_status = new_status
            if new_status == 'DELIVERED':
                order.payment_status = 'PAID'
            order.save()
            messages.success(request, f"Order #{order.order_number} updated to {order.get_order_status_display()}.")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:owner_dashboard')
