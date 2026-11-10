from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GroupOrder, GroupMember, GroupOrderItem
from restaurants.models import Restaurant
from menu.models import FoodItem
from orders.models import Order, OrderItem
from accounts.decorators import customer_required


@login_required
@customer_required
def group_order_list(request):
    hosted_groups = GroupOrder.objects.filter(host=request.user)
    joined_groups = GroupOrder.objects.filter(members__user=request.user).exclude(host=request.user).distinct()
    restaurants = Restaurant.objects.filter(is_active=True)

    return render(request, 'group_orders/group_list.html', {
        'hosted_groups': hosted_groups,
        'joined_groups': joined_groups,
        'restaurants': restaurants,
    })


@login_required
@customer_required
def create_group_order(request):
    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        title = request.POST.get('title', '').strip() or "Campus Friends Feast"
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id, is_active=True)

        group = GroupOrder.objects.create(
            host=request.user,
            restaurant=restaurant,
            title=title
        )
        # Add host as first member
        GroupMember.objects.create(group_order=group, user=request.user)

        messages.success(request, f"Group Order created! Share code '{group.group_code}' with your friends.")
        return redirect('group_orders:group_order_detail', group_code=group.group_code)

    return redirect('group_orders:group_order_list')


@login_required
@customer_required
def join_group_order(request):
    if request.method == 'POST':
        code = request.POST.get('group_code', '').strip().upper()
        group = GroupOrder.objects.filter(group_code=code, status='OPEN').first()

        if not group:
            messages.error(request, f"No active open group order found for code '{code}'.")
            return redirect('group_orders:group_order_list')

        member, created = GroupMember.objects.get_or_create(group_order=group, user=request.user)
        if created:
            messages.success(request, f"You successfully joined group order '{group.title}'!")
        else:
            messages.info(request, f"You are already a member of '{group.title}'.")

        return redirect('group_orders:group_order_detail', group_code=group.group_code)

    return redirect('group_orders:group_order_list')


@login_required
@customer_required
def group_order_detail(request, group_code):
    group = get_object_or_404(GroupOrder.objects.select_related('host', 'restaurant'), group_code=group_code.upper())
    
    # Check if current user is in group
    user_member = GroupMember.objects.filter(group_order=group, user=request.user).first()
    if not user_member and request.user != group.host and not request.user.is_superuser:
        messages.warning(request, "Please join the group using its invitation code first.")
        return redirect('group_orders:group_order_list')

    members = group.members.select_related('user').prefetch_related('items__food_item').all()
    menu_items = group.restaurant.food_items.filter(is_available=True)

    # Compute breakdown per member
    breakdown = []
    total_bill = 0
    for m in members:
        m_items = m.items.select_related('food_item').all()
        m_total = sum(i.item_total() for i in m_items)
        total_bill += m_total
        breakdown.append({
            'member': m,
            'items': m_items,
            'total': m_total
        })

    return render(request, 'group_orders/group_detail.html', {
        'group': group,
        'breakdown': breakdown,
        'total_bill': total_bill,
        'menu_items': menu_items,
        'user_member': user_member,
        'is_host': (request.user == group.host),
    })


@login_required
@customer_required
def add_item_to_group(request, group_code):
    group = get_object_or_404(GroupOrder, group_code=group_code.upper(), status='OPEN')
    member = get_object_or_404(GroupMember, group_order=group, user=request.user)

    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        qty = int(request.POST.get('quantity', 1))
        notes = request.POST.get('notes', '').strip()

        food = get_object_or_404(FoodItem, pk=food_id, restaurant=group.restaurant, is_available=True)

        existing = GroupOrderItem.objects.filter(group_order=group, member=member, food_item=food).first()
        if existing:
            existing.quantity += qty
            existing.save()
        else:
            GroupOrderItem.objects.create(
                group_order=group,
                member=member,
                food_item=food,
                quantity=qty,
                special_notes=notes
            )

        messages.success(request, f"Added {qty}x {food.name} to your group plate!")

    return redirect('group_orders:group_order_detail', group_code=group.group_code)


@login_required
@customer_required
def remove_group_item(request, item_id):
    item = get_object_or_404(GroupOrderItem.objects.select_related('group_order', 'member__user'), pk=item_id)
    group = item.group_order

    # Only member or host can remove
    if request.user == item.member.user or request.user == group.host:
        item.delete()
        messages.info(request, "Item removed from group order.")
    else:
        messages.error(request, "You can only remove your own items.")

    return redirect('group_orders:group_order_detail', group_code=group.group_code)


@login_required
@customer_required
def checkout_group_order(request, group_code):
    group = get_object_or_404(GroupOrder, group_code=group_code.upper(), host=request.user)

    if group.status != 'OPEN':
        messages.warning(request, "This group order is already locked or placed.")
        return redirect('group_orders:group_order_detail', group_code=group.group_code)

    all_items = group.order_items.select_related('food_item', 'member__user').all()
    if not all_items.exists():
        messages.error(request, "No items have been added to the group order yet.")
        return redirect('group_orders:group_order_detail', group_code=group.group_code)

    total_bill = sum(i.item_total() for i in all_items)

    if request.method == 'POST':
        address = request.POST.get('delivery_address', '').strip()
        phone = request.POST.get('contact_phone', '').strip()

        if not address or not phone:
            messages.error(request, "Delivery address and host contact phone are required.")
            return redirect('group_orders:checkout_group_order', group_code=group.group_code)

        # Create master Order
        order = Order.objects.create(
            user=request.user,
            restaurant=group.restaurant,
            total_amount=total_bill,
            delivery_address=address,
            contact_phone=phone,
            payment_method='COD',
            payment_status='UNPAID',
            order_status='PENDING',
            special_instructions=f"Group Order ({group.title}) - Code: {group.group_code}"
        )

        for gi in all_items:
            OrderItem.objects.create(
                order=order,
                food_item=gi.food_item,
                food_name=f"{gi.food_item.name} (for {gi.member.user.username})",
                price=gi.food_item.price,
                quantity=gi.quantity
            )

        group.status = 'PLACED'
        group.delivery_address = address
        group.save()

        messages.success(request, f"Group Order placed successfully! Master Order #{order.order_number}")
        return redirect('orders:order_detail', order_number=order.order_number)

    return render(request, 'group_orders/group_checkout.html', {
        'group': group,
        'all_items': all_items,
        'total_bill': total_bill,
    })
