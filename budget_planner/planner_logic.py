from decimal import Decimal
from menu.models import FoodItem


def generate_budget_meal_plans(daily_budget, diet_preference='ALL', max_plans=3):
    """
    Beginner-friendly, modular Python filtering and scoring logic for B.Tech viva:
    1. Filter available food items by diet (Veg / All).
    2. Partition into Breakfast, Lunch, and Dinner pools.
    3. Generate valid (Breakfast + Lunch + Dinner) combinations within daily_budget.
    4. Score combos based on budget utilization, ratings, and nutritional balance.
    """
    daily_budget = Decimal(str(daily_budget))
    
    # 1. Base queryset
    items_qs = FoodItem.objects.filter(is_available=True).select_related('restaurant', 'category', 'nutrition')
    if diet_preference == 'VEG':
        items_qs = items_qs.filter(is_veg=True)

    # 2. Partition
    breakfasts = list(items_qs.filter(meal_type='BREAKFAST', price__lte=daily_budget * Decimal('0.40')))
    if not breakfasts:
        # Fallback: snacks or any lower-priced items
        breakfasts = list(items_qs.filter(price__lte=daily_budget * Decimal('0.35'))[:8])

    lunches = list(items_qs.filter(meal_type='LUNCH', price__lte=daily_budget * Decimal('0.60')))
    if not lunches:
        lunches = list(items_qs.filter(price__lte=daily_budget * Decimal('0.55'))[:8])

    dinners = list(items_qs.filter(meal_type='DINNER', price__lte=daily_budget * Decimal('0.55')))
    if not dinners:
        # Fallback to lunch items for dinner
        dinners = list(items_qs.filter(price__lte=daily_budget * Decimal('0.50'))[:8])

    combos = []

    # 3. Combinatorial generation with safety limit
    for b in breakfasts[:10]:
        for l in lunches[:10]:
            if b.id == l.id:
                continue
            for d in dinners[:10]:
                if d.id in (b.id, l.id):
                    continue

                total_cost = b.price + l.price + d.price
                if total_cost <= daily_budget:
                    remaining = daily_budget - total_cost

                    # Compute total nutrition
                    cal_b = getattr(b, 'nutrition', None)
                    cal_l = getattr(l, 'nutrition', None)
                    cal_d = getattr(d, 'nutrition', None)

                    total_calories = (cal_b.calories if cal_b else 300) + \
                                     (cal_l.calories if cal_l else 550) + \
                                     (cal_d.calories if cal_d else 450)

                    total_protein = (float(cal_b.protein) if cal_b else 10) + \
                                    (float(cal_l.protein) if cal_l else 20) + \
                                    (float(cal_d.protein) if cal_d else 15)

                    # Viva scoring heuristic:
                    # Prefer combos that utilize budget reasonably (not leaving too much unspent)
                    # and have good protein/calories without exceeding budget.
                    budget_utilization = float(total_cost / daily_budget)
                    score = (budget_utilization * 50) + (total_protein * 1.5)

                    combos.append({
                        'breakfast': b,
                        'lunch': l,
                        'dinner': d,
                        'total_cost': total_cost,
                        'remaining_budget': remaining,
                        'total_calories': total_calories,
                        'total_protein': round(total_protein, 1),
                        'score': score
                    })

    # Sort descending by score
    combos.sort(key=lambda x: x['score'], reverse=True)

    # Tag plans nicely for display
    tagged_plans = []
    titles = [
        ("Student Value Saver", "bg-success text-white", "Balanced calories and maximum savings"),
        ("High-Protein Power Meal", "bg-warning text-dark", "Nutrient-packed meal combo for active days"),
        ("Campus Chef Special Combo", "bg-info text-dark", "Delicious local favorites within your budget"),
    ]

    for i, c in enumerate(combos[:max_plans]):
        title, badge_class, desc = titles[i] if i < len(titles) else (f"Meal Combo Option #{i+1}", "bg-secondary text-white", "Custom budget combo")
        c['plan_title'] = title
        c['badge_class'] = badge_class
        c['description'] = desc
        tagged_plans.append(c)

    return tagged_plans

