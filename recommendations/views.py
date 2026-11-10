from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .engine import get_ai_food_recommendations
from .models import UserFoodPreference
from menu.models import FoodCategory


@login_required
def recommendations_view(request):
    pref, _ = UserFoodPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        is_veg = request.POST.get('is_vegetarian') == '1'
        cal_pref = request.POST.get('calorie_preference', 'ANY')
        pref.is_vegetarian = is_veg
        pref.calorie_preference = cal_pref
        pref.save()
        messages.success(request, "AI preferences updated! Recomputing recommendations...")
        return redirect('recommendations:recommendations_view')

    recommended_items = get_ai_food_recommendations(user=request.user, top_n=8)
    categories = FoodCategory.objects.all()

    return render(request, 'recommendations/recommendations.html', {
        'recommendations': recommended_items,
        'pref': pref,
        'categories': categories,
    })
