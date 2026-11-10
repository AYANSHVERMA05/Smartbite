from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, Subscription
from accounts.decorators import customer_required


def plan_list(request):
    duration = request.GET.get('duration')
    plan_type = request.GET.get('type')

    plans = SubscriptionPlan.objects.filter(is_active=True).select_related('restaurant')

    if duration:
        plans = plans.filter(duration_type=duration)

    if plan_type:
        plans = plans.filter(plan_type=plan_type)

    return render(request, 'subscriptions/plan_list.html', {
        'plans': plans,
        'selected_duration': duration,
        'selected_type': plan_type,
    })


@login_required
@customer_required
def subscribe(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
    profile = getattr(request.user, 'customer_profile', None)
    default_address = profile.hostel_block_room if profile and profile.hostel_block_room else ''

    if request.method == 'POST':
        hostel_address = request.POST.get('hostel_address', '').strip()
        if not hostel_address:
            messages.error(request, "Please enter your Hostel Block & Room number for daily mess meal delivery.")
            return render(request, 'subscriptions/subscribe.html', {'plan': plan, 'default_address': default_address})

        days = 7 if plan.duration_type == 'WEEKLY' else 30
        end_date = timezone.now().date() + timedelta(days=days)

        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            end_date=end_date,
            delivery_hostel_address=hostel_address,
            status='ACTIVE'
        )

        messages.success(request, f"Subscribed successfully to '{plan.name}'! Valid until {end_date.strftime('%d %b %Y')}.")
        return redirect('subscriptions:my_subscriptions')

    return render(request, 'subscriptions/subscribe.html', {
        'plan': plan,
        'default_address': default_address,
    })


@login_required
@customer_required
def my_subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user).select_related('plan', 'plan__restaurant')
    return render(request, 'subscriptions/my_subscriptions.html', {
        'subscriptions': subscriptions,
        'today': timezone.now().date(),
    })


@login_required
@customer_required
def cancel_subscription(request, sub_id):
    sub = get_object_or_404(Subscription, pk=sub_id, user=request.user)
    if sub.status == 'ACTIVE':
        sub.status = 'CANCELLED'
        sub.save()
        messages.info(request, f"Subscription for '{sub.plan.name}' has been cancelled.")
    return redirect('subscriptions:my_subscriptions')
