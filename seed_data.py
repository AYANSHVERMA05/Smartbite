import os
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartbite_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile
from restaurants.models import Restaurant
from menu.models import FoodCategory, FoodItem, Review
from nutrition.models import FoodNutrition
from surplus_food.models import SurplusFood
from subscriptions.models import SubscriptionPlan
from recommendations.models import UserFoodPreference
from orders.models import Cart

User = get_user_model()


def seed():
    print("🌱 Starting SmartBite database seeding...")

    # 1. Create Superuser / Admin
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@smartbite.edu',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'phone': '9876500000'
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()
    print("✓ Created Admin: admin / admin123")

    # 2. Create Students (Customers)
    rahul, _ = User.objects.get_or_create(
        username='rahul',
        defaults={'email': 'rahul@campus.edu', 'role': 'CUSTOMER', 'phone': '9876511111'}
    )
    rahul.set_password('student123')
    rahul.save()
    cp_rahul, _ = CustomerProfile.objects.get_or_create(
        user=rahul,
        defaults={
            'delivery_address': 'Tagore Hostel, Block B, Room 204',
            'hostel_block_room': 'Block B, Room 204',
            'preferred_diet': 'ALL',
            'daily_budget_limit': Decimal('350.00')
        }
    )
    Cart.objects.get_or_create(user=rahul)
    UserFoodPreference.objects.get_or_create(user=rahul, defaults={'is_vegetarian': False})

    priya, _ = User.objects.get_or_create(
        username='priya',
        defaults={'email': 'priya@campus.edu', 'role': 'CUSTOMER', 'phone': '9876522222'}
    )
    priya.set_password('student123')
    priya.save()
    cp_priya, _ = CustomerProfile.objects.get_or_create(
        user=priya,
        defaults={
            'delivery_address': 'Gargi Girls Hostel, Block A, Room 102',
            'hostel_block_room': 'Block A, Room 102',
            'preferred_diet': 'VEG',
            'daily_budget_limit': Decimal('300.00')
        }
    )
    Cart.objects.get_or_create(user=priya)
    UserFoodPreference.objects.get_or_create(user=priya, defaults={'is_vegetarian': True})
    print("✓ Created Students: rahul / student123 & priya / student123")

    # 3. Create Restaurant Owners
    owner1, _ = User.objects.get_or_create(
        username='owner_spicedhaba',
        defaults={'email': 'spicedhaba@campus.edu', 'role': 'RESTAURANT_OWNER', 'phone': '9876533333'}
    )
    owner1.set_password('owner123')
    owner1.save()

    owner2, _ = User.objects.get_or_create(
        username='owner_greenbowl',
        defaults={'email': 'greenbowl@campus.edu', 'role': 'RESTAURANT_OWNER', 'phone': '9876544444'}
    )
    owner2.set_password('owner123')
    owner2.save()
    print("✓ Created Restaurant Owners: owner_spicedhaba / owner123 & owner_greenbowl / owner123")

    # 4. Create Restaurants
    rest1, _ = Restaurant.objects.get_or_create(
        owner=owner1,
        defaults={
            'name': 'Desi Spice Dhaba & Canteen',
            'description': 'Authentic North Indian curries, aromatic biryanis, warm parathas and student thalis.',
            'address': 'Campus Central Food Court, Stall #4',
            'phone': '9876533333',
            'cuisine_type': 'North Indian & Mughlai',
            'rating': Decimal('4.8'),
            'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=700',
            'is_active': True
        }
    )

    rest2, _ = Restaurant.objects.get_or_create(
        owner=owner2,
        defaults={
            'name': 'The Green Bowl & Fitness Café',
            'description': 'Nutritious high-protein bowls, fresh salads, wholesome wraps, smoothies and diet meals.',
            'address': 'Sports Complex Arcade, Ground Floor',
            'phone': '9876544444',
            'cuisine_type': 'Healthy & Continental',
            'rating': Decimal('4.6'),
            'image_url': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=700',
            'is_active': True
        }
    )
    print("✓ Created Campus Restaurants")

    # 5. Food Categories
    categories = {
        'North Indian': ('fa-bowl-rice', 'Rich gravies, paneer, dals and Indian breads', 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400'),
        'Healthy Bowls': ('fa-leaf', 'Calorie-counted salads and protein-rich bowls', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400'),
        'South Indian & Breakfast': ('fa-mug-hot', 'Crispy dosas, idlis, poha and filter coffee', 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400'),
        'Fast Food & Rolls': ('fa-burger', 'Frankies, wraps, burgers and quick bites', 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=400'),
        'Beverages & Shakes': ('fa-glass-water', 'Fresh fruit juices, lassi, shakes and cold brew', 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=400'),
    }
    cat_objs = {}
    for name, (icon, desc, img) in categories.items():
        c, _ = FoodCategory.objects.get_or_create(
            name=name,
            defaults={'icon': icon, 'description': desc, 'image_url': img}
        )
        cat_objs[name] = c

    # 6. Food Items + Nutrition Facts
    food_data = [
        # Desi Spice Dhaba
        {
            'restaurant': rest1,
            'category': cat_objs['South Indian & Breakfast'],
            'name': 'Aloo Paratha with Curd & Pickle',
            'description': 'Two golden tawa-cooked whole wheat parathas stuffed with spiced potatoes, served with fresh curd and spicy pickle.',
            'price': Decimal('70.00'),
            'meal_type': 'BREAKFAST',
            'is_veg': True,
            'prep': 15,
            'img': 'https://images.unsplash.com/photo-1626074353765-517a681e40be?w=500',
            'cal': 380, 'pro': 8.5, 'carb': 54.0, 'fat': 14.0, 'tag': 'Campus Breakfast'
        },
        {
            'restaurant': rest1,
            'category': cat_objs['North Indian'],
            'name': 'Special Deluxe Student Thali',
            'description': 'Wholesome student meal: Dal Makhani, Paneer Butter Masala, 3 Butter Rotis, Steamed Jeera Rice and Salad.',
            'price': Decimal('140.00'),
            'meal_type': 'LUNCH',
            'is_veg': True,
            'prep': 20,
            'img': 'https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=500',
            'cal': 680, 'pro': 22.0, 'carb': 88.0, 'fat': 18.0, 'tag': 'High Protein, Balanced Diet'
        },
        {
            'restaurant': rest1,
            'category': cat_objs['North Indian'],
            'name': 'Paneer Butter Masala & 2 Naan',
            'description': 'Soft cottage cheese cubes cooked in creamy tomato butter gravy with garlic naan bread.',
            'price': Decimal('160.00'),
            'meal_type': 'DINNER',
            'is_veg': True,
            'prep': 25,
            'img': 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500',
            'cal': 620, 'pro': 19.5, 'carb': 65.0, 'fat': 22.0, 'tag': 'Student Favorite'
        },
        {
            'restaurant': rest1,
            'category': cat_objs['North Indian'],
            'name': 'Hyderabadi Chicken Dum Biryani',
            'description': 'Fragrant basmati rice layered with succulent marinated chicken and authentic spices, served with cooling raita.',
            'price': Decimal('180.00'),
            'meal_type': 'LUNCH',
            'is_veg': False,
            'prep': 25,
            'img': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500',
            'cal': 720, 'pro': 34.0, 'carb': 82.0, 'fat': 20.0, 'tag': 'High Protein'
        },
        {
            'restaurant': rest1,
            'category': cat_objs['North Indian'],
            'name': 'Homestyle Yellow Dal Khichdi',
            'description': 'Light, comforting and easy to digest moong dal khichdi tempered with cumin and desi ghee.',
            'price': Decimal('90.00'),
            'meal_type': 'DINNER',
            'is_veg': True,
            'prep': 15,
            'img': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500',
            'cal': 390, 'pro': 14.0, 'carb': 62.0, 'fat': 7.0, 'tag': 'Low Calorie, Comfort Food'
        },
        {
            'restaurant': rest1,
            'category': cat_objs['Beverages & Shakes'],
            'name': 'Sweet Punjabi Lassi',
            'description': 'Thick and creamy churned yogurt drink topped with a dollop of fresh malai.',
            'price': Decimal('50.00'),
            'meal_type': 'SNACK',
            'is_veg': True,
            'prep': 5,
            'img': 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500',
            'cal': 220, 'pro': 6.0, 'carb': 32.0, 'fat': 7.5, 'tag': 'Beverage'
        },

        # The Green Bowl & Fitness Café
        {
            'restaurant': rest2,
            'category': cat_objs['South Indian & Breakfast'],
            'name': 'Masala Oats & Sprout Bowl',
            'description': 'Warm spiced rolled oats with steamed moong sprouts, roasted peanuts and lemon herbs.',
            'price': Decimal('80.00'),
            'meal_type': 'BREAKFAST',
            'is_veg': True,
            'prep': 10,
            'img': 'https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=500',
            'cal': 310, 'pro': 16.0, 'carb': 48.0, 'fat': 6.0, 'tag': 'High Protein, Low Calorie'
        },
        {
            'restaurant': rest2,
            'category': cat_objs['Healthy Bowls'],
            'name': 'Grilled Paneer Protein Power Bowl',
            'description': 'Marinated grilled paneer cubes, quinoa, sweet corn, cherry tomatoes, cucumbers and greek yogurt dressing.',
            'price': Decimal('170.00'),
            'meal_type': 'LUNCH',
            'is_veg': True,
            'prep': 15,
            'img': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500',
            'cal': 480, 'pro': 28.0, 'carb': 42.0, 'fat': 15.0, 'tag': 'High Protein, Gym Fuel'
        },
        {
            'restaurant': rest2,
            'category': cat_objs['Healthy Bowls'],
            'name': 'Grilled Chicken Caesar Salad Bowl',
            'description': 'Herb-grilled chicken breast slices over crisp lettuce, croutons, parmesan and olive oil caesar dressing.',
            'price': Decimal('190.00'),
            'meal_type': 'DINNER',
            'is_veg': False,
            'prep': 20,
            'img': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500',
            'cal': 440, 'pro': 38.0, 'carb': 18.0, 'fat': 12.0, 'tag': 'High Protein, Keto Friendly'
        },
        {
            'restaurant': rest2,
            'category': cat_objs['Fast Food & Rolls'],
            'name': 'Whole Wheat Veggie Paneer Wrap',
            'description': 'Crispy grilled whole-wheat wrap packed with tandoori spiced cottage cheese, bell peppers and mint mayo.',
            'price': Decimal('110.00'),
            'meal_type': 'SNACK',
            'is_veg': True,
            'prep': 12,
            'img': 'https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=500',
            'cal': 370, 'pro': 15.0, 'carb': 45.0, 'fat': 11.0, 'tag': 'Healthy Snack'
        },
    ]

    for item_data in food_data:
        food, _ = FoodItem.objects.get_or_create(
            restaurant=item_data['restaurant'],
            name=item_data['name'],
            defaults={
                'category': item_data['category'],
                'description': item_data['description'],
                'price': item_data['price'],
                'meal_type': item_data['meal_type'],
                'is_veg': item_data['is_veg'],
                'preparation_time': item_data['prep'],
                'image_url': item_data['img'],
                'is_available': True
            }
        )
        FoodNutrition.objects.get_or_create(
            food_item=food,
            defaults={
                'calories': item_data['cal'],
                'protein': Decimal(str(item_data['pro'])),
                'carbohydrates': Decimal(str(item_data['carb'])),
                'fat': Decimal(str(item_data['fat'])),
                'dietary_tags': item_data['tag']
            }
        )
    print("✓ Created 10 Campus Food Items with Complete Nutritional Data")

    # 7. Surplus Food Listings (Food Waste Reduction)
    now = timezone.now()
    surplus_items = [
        {
            'restaurant': rest1,
            'food_name': 'Evening Dal Makhani & Jeera Rice (Fresh Surplus)',
            'orig': Decimal('140.00'),
            'disc': Decimal('70.00'),
            'qty': 6,
            'hours': 4,
            'veg': True,
            'img': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500',
            'desc': 'Freshly prepared evening batch. Packaged hygienically. Help us eliminate food waste on campus!'
        },
        {
            'restaurant': rest2,
            'food_name': 'Nutrient Salad Bowls Batch (50% Off)',
            'orig': Decimal('160.00'),
            'disc': Decimal('80.00'),
            'qty': 4,
            'hours': 3,
            'veg': True,
            'img': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500',
            'desc': 'Fresh organic salad bowls prepared today. Collect at sports complex arcade before 9 PM.'
        }
    ]

    for sp in surplus_items:
        SurplusFood.objects.get_or_create(
            restaurant=sp['restaurant'],
            food_name=sp['food_name'],
            defaults={
                'original_price': sp['orig'],
                'discounted_price': sp['disc'],
                'available_quantity': sp['qty'],
                'pickup_deadline': now + timedelta(hours=sp['hours']),
                'is_veg': sp['veg'],
                'image_url': sp['img'],
                'description': sp['desc'],
                'is_active': True
            }
        )
    print("✓ Created Active Surplus Food Listings (Zero Waste)")

    # 8. Hostel Mess Subscription Plans
    plans = [
        {
            'restaurant': rest1,
            'name': 'Hostel Royal Monthly Mess (Lunch & Dinner)',
            'duration': 'MONTHLY',
            'coverage': 'LUNCH_DINNER',
            'type': 'VEG',
            'price': Decimal('3200.00'),
            'desc': 'Complete hassle-free monthly dining delivered directly to your hostel wing. 4 rotis, 2 subzis, dal, rice, salad & sweet.',
            'features': 'Daily Room Delivery to Hostel Gate\nUnlimited Steamed Rice & Warm Rotis\nSunday Special Dessert & Paneer\nPause or resume anytime during semester exams'
        },
        {
            'restaurant': rest1,
            'name': 'Weekly Express Mess Trial (7 Days)',
            'duration': 'WEEKLY',
            'coverage': 'LUNCH_DINNER',
            'type': 'VEG',
            'price': Decimal('850.00'),
            'desc': 'A quick 7-day trial of our homestyle kitchen meals before committing to a full monthly subscription.',
            'features': '7 Days of fresh Lunch and Dinner\nZero Delivery Charge\nHomestyle hygienic cooking'
        },
        {
            'restaurant': rest2,
            'name': 'Athlete & Fitness Monthly Meal Pass',
            'duration': 'MONTHLY',
            'coverage': 'ALL_THREE',
            'type': 'COMBO',
            'price': Decimal('4200.00'),
            'desc': 'High protein breakfast, calorie-controlled lunch and light nutritious dinner designed for sports players and gym-goers.',
            'features': 'Breakfast: Oats/Sprouts/Eggs\nLunch: Quinoa & Grilled Protein Bowl\nDinner: Light Salad & Protein Wrap\nMacro & Calorie tracked daily'
        }
    ]

    for p in plans:
        SubscriptionPlan.objects.get_or_create(
            restaurant=p['restaurant'],
            name=p['name'],
            defaults={
                'duration_type': p['duration'],
                'meal_coverage': p['coverage'],
                'plan_type': p['type'],
                'price': p['price'],
                'description': p['desc'],
                'features': p['features'],
                'is_active': True
            }
        )
    print("✓ Created Hostel Mess Subscription Plans")

    # 9. Sample Customer Reviews
    f1 = FoodItem.objects.filter(name__icontains='Deluxe Student Thali').first()
    if f1:
        Review.objects.get_or_create(
            food_item=f1,
            user=rahul,
            defaults={'rating': 5, 'comment': 'Best value thali in the entire campus! Dal Makhani is extremely tasty and portions are generous.', 'restaurant': f1.restaurant}
        )

    f2 = FoodItem.objects.filter(name__icontains='Protein Power Bowl').first()
    if f2:
        Review.objects.get_or_create(
            food_item=f2,
            user=priya,
            defaults={'rating': 5, 'comment': 'Great post-workout meal. Clean ingredients, very fresh cottage cheese, highly recommended.', 'restaurant': f2.restaurant}
        )
    print("✓ Created Sample Reviews")

    print("\n🎉 SMARTBITE DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("---------------------------------------------------------")
    print("DEMO CREDENTIALS FOR TESTING & VIVA:")
    print("1. Student / Customer:        username: rahul             password: student123")
    print("2. Student / Customer (Veg):  username: priya             password: student123")
    print("3. Restaurant Owner 1:        username: owner_spicedhaba  password: owner123")
    print("4. Restaurant Owner 2:        username: owner_greenbowl   password: owner123")
    print("5. System Administrator:      username: admin             password: admin123")
    print("---------------------------------------------------------")


if __name__ == '__main__':
    seed()
