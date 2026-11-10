from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import CustomerProfile
from orders.models import Cart
from recommendations.models import UserFoodPreference
from restaurants.models import Restaurant


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            if user.role == 'CUSTOMER':
                # Create profile
                CustomerProfile.objects.create(
                    user=user,
                    hostel_block_room=form.cleaned_data.get('hostel_block_room', ''),
                    preferred_diet=form.cleaned_data.get('preferred_diet', 'ALL'),
                    delivery_address=form.cleaned_data.get('hostel_block_room', '')
                )
                # Create user cart
                Cart.objects.get_or_create(user=user)
                # Create user food preference
                UserFoodPreference.objects.get_or_create(
                    user=user,
                    is_vegetarian=(form.cleaned_data.get('preferred_diet') == 'VEG')
                )
                messages.success(request, f"Welcome to SmartBite, {user.username}! Your student account has been created.")
            elif user.role == 'RESTAURANT_OWNER':
                r_name = form.cleaned_data.get('restaurant_name') or f"{user.username}'s Kitchen"
                r_addr = form.cleaned_data.get('restaurant_address') or "Campus Food Court"
                Restaurant.objects.create(
                    owner=user,
                    name=r_name,
                    description=f"Fresh, hygienic and delicious meals prepared by {r_name}.",
                    address=r_addr,
                    phone=user.phone or "N/A",
                    cuisine_type="Multi-Cuisine",
                    image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=700"
                )
                messages.success(request, f"Restaurant partner account created for {r_name}!")
            
            # Automatically log in
            login(request, user)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('menu:home')


def quick_login_view(request, role_key):
    """
    Convenient Viva and Evaluation feature:
    One-click instant login for students, customers, restaurant owners and admin.
    """
    role_map = {
        'student': 'rahul',
        'customer': 'rahul',
        'student_veg': 'priya',
        'owner': 'owner_spicedhaba',
        'restaurant_owner': 'owner_spicedhaba',
        'owner_greenbowl': 'owner_greenbowl',
        'admin': 'admin',
    }
    username = role_map.get(role_key.lower())
    if not username:
        messages.error(request, "Invalid demo role selected.")
        return redirect('accounts:login')

    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        login(request, user)
        messages.success(request, f"Signed in as {user.get_role_display()}: {user.username}")
        return redirect('accounts:dashboard_redirect')
    except User.DoesNotExist:
        messages.error(request, f"User '{username}' not found. Please run seed_data.py first.")
        return redirect('accounts:login')


@login_required
def dashboard_redirect(request):
    if request.user.is_admin_user:
        return redirect('dashboard:admin_dashboard')
    elif request.user.is_restaurant_owner:
        return redirect('dashboard:owner_dashboard')
    else:
        return redirect('dashboard:customer_dashboard')


@login_required
def profile_view(request):
    user = request.user
    profile, _ = CustomerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            user.phone = form.cleaned_data['phone']
            user.save()
            form.save()

            # Update food preference sync
            if hasattr(user, 'food_preference'):
                user.food_preference.is_vegetarian = (profile.preferred_diet == 'VEG')
                user.food_preference.save()

            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile, initial={'email': user.email, 'phone': user.phone})

    return render(request, 'accounts/profile.html', {'form': form, 'user_obj': user, 'profile': profile})
