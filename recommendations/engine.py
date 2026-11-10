import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from menu.models import FoodItem
from orders.models import OrderItem
from .models import UserFoodPreference


def get_price_tier(price):
    if price < 100:
        return 'budget_cheap'
    elif price <= 220:
        return 'budget_medium'
    else:
        return 'budget_premium'


def build_food_features(food_item):
    cat_name = food_item.category.name if food_item.category else 'General'
    diet = 'vegetarian veg plant' if food_item.is_veg else 'nonvegetarian nonveg meat'
    meal = food_item.meal_type.lower()
    price_tier = get_price_tier(food_item.price)
    
    nut_tags = ''
    if hasattr(food_item, 'nutrition') and food_item.nutrition:
        nut_tags = food_item.nutrition.dietary_tags

    # Combined textual bag of features for TF-IDF
    features = f"{cat_name} {cat_name} {diet} {diet} {meal} {price_tier} {food_item.name} {nut_tags}"
    return features.lower()


def get_ai_food_recommendations(user, top_n=6):
    """
    Academic Viva Explanation:
    Content-Based Recommendation Engine using Scikit-learn TF-IDF & Cosine Similarity.
    1. Extracts metadata features (Category, Veg/Non-Veg, Meal Type, Price Bracket, Nutritional Tags)
    2. Constructs User Profile from past OrderItem history + explicit UserFoodPreference.
    3. Calculates Cosine Similarity between user profile vector and food item matrix.
    4. Provides fallback to highest rated popular items for cold-start (new users).
    """
    candidate_items = list(FoodItem.objects.filter(is_available=True).select_related('restaurant', 'category', 'nutrition'))
    if not candidate_items:
        return []

    # Get user preference
    pref, _ = UserFoodPreference.objects.get_or_create(user=user)
    is_veg_only = pref.is_vegetarian

    # 1. Fetch user order history
    past_orders = OrderItem.objects.filter(order__user=user).select_related('food_item', 'food_item__category')
    ordered_items = [o.food_item for o in past_orders if o.food_item]

    # Cold-start check
    if not ordered_items:
        # Fallback: popular items filtered by diet
        results = []
        for item in candidate_items:
            if is_veg_only and not item.is_veg:
                continue
            reason = "Popular campus favorite with top ratings among students."
            if is_veg_only:
                reason = "Highly rated pure vegetarian option popular on campus."
            results.append({
                'item': item,
                'similarity_score': 0.85,
                'explanation': reason,
                'is_personalized': False
            })
            if len(results) >= top_n:
                break
        return results

    # Personalized Recommendation:
    # Build text descriptions for candidates
    candidate_texts = [build_food_features(item) for item in candidate_items]

    # Build user text profile from past orders
    user_tokens = []
    top_categories = {}
    for item in ordered_items:
        user_tokens.append(build_food_features(item))
        if item.category:
            top_categories[item.category.name] = top_categories.get(item.category.name, 0) + 1

    most_favored_cat = max(top_categories, key=top_categories.get) if top_categories else "Specialties"
    user_profile_text = " ".join(user_tokens)

    # Scikit-learn TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    # Fit on all documents + user profile
    all_docs = [user_profile_text] + candidate_texts
    tfidf_matrix = vectorizer.fit_transform(all_docs)

    user_vec = tfidf_matrix[0:1]
    candidate_matrix = tfidf_matrix[1:]

    # Cosine Similarity calculation
    sim_scores = cosine_similarity(user_vec, candidate_matrix).flatten()

    # Pair items with similarity
    scored_items = []
    for idx, score in enumerate(sim_scores):
        item = candidate_items[idx]
        
        # Apply strict vegetarian constraint if selected
        if is_veg_only and not item.is_veg:
            continue

        # Adjust score slightly with average rating
        adjusted_score = float(score) * 0.7 + (float(item.average_rating) / 5.0) * 0.3

        # Formulate meaningful reason for Viva
        item_cat = item.category.name if item.category else "Food"
        if item_cat in top_categories:
            reason = f"Matches your taste for {item_cat} based on your previous orders."
        elif is_veg_only and item.is_veg:
            reason = f"Recommended based on your vegetarian preference and top reviews."
        else:
            reason = f"Similar meal profile and price bracket to dishes you recently enjoyed."

        scored_items.append({
            'item': item,
            'similarity_score': round(adjusted_score, 2),
            'explanation': reason,
            'is_personalized': True
        })

    # Sort descending by similarity
    scored_items.sort(key=lambda x: x['similarity_score'], reverse=True)
    return scored_items[:top_n]

