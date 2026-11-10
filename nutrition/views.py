from django.shortcuts import render
from menu.models import FoodItem, FoodCategory
from .models import FoodNutrition
from django.db.models import Q


def nutrition_filter_view(request):
    max_cal = request.GET.get('max_calories', '').strip()
    min_pro = request.GET.get('min_protein', '').strip()
    is_veg = request.GET.get('is_veg', '').strip()
    selected_tag = request.GET.get('tag', '').strip()

    items = FoodItem.objects.filter(is_available=True).select_related('nutrition', 'restaurant', 'category')

    if max_cal:
        try:
            items = items.filter(nutrition__calories__lte=int(max_cal))
        except ValueError:
            pass

    if min_pro:
        try:
            items = items.filter(nutrition__protein__gte=float(min_pro))
        except ValueError:
            pass

    if is_veg == '1':
        items = items.filter(is_veg=True)
    elif is_veg == '0':
        items = items.filter(is_veg=False)

    if selected_tag:
        items = items.filter(nutrition__dietary_tags__icontains=selected_tag)

    return render(request, 'nutrition/nutrition_filter.html', {
        'items': items,
        'max_cal': max_cal,
        'min_pro': min_pro,
        'is_veg': is_veg,
        'selected_tag': selected_tag,
    })
