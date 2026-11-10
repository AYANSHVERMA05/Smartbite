import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartbite_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def run_tests():
    print("🧪 Running SmartBite Comprehensive Test Suite...\n")
    client = Client()

    # Public pages
    public_urls = [
        ('/', "Home Page"),
        ('/menu/', "Food Menu Listing"),
        ('/restaurants/', "Restaurants Listing"),
        ('/budget-planner/', "Smart Budget Meal Planner"),
        ('/nutrition/filter/', "Nutrition Filter"),
        ('/surplus-food/', "Surplus Food Deals"),
        ('/subscriptions/plans/', "Mess Subscription Plans"),
        ('/accounts/login/', "Login Page"),
        ('/accounts/register/', "Registration Page"),
    ]

    for url, name in public_urls:
        res = client.get(url)
        assert res.status_code == 200, f"Failed on {name} ({url}): HTTP {res.status_code}"
        print(f"  ✓ [200 OK] {name} ({url})")

    # Customer Authenticated Tests
    customer = User.objects.get(username='rahul')
    client.force_login(customer)

    customer_urls = [
        ('/orders/cart/', "Shopping Cart"),
        ('/orders/history/', "Order History"),
        ('/group-orders/', "Group Orders Hub"),
        ('/surplus-food/my-bookings/', "My Surplus Bookings"),
        ('/subscriptions/my-subscriptions/', "My Mess Subscriptions"),
        ('/recommendations/', "AI Food Recommendations Engine"),
        ('/dashboard/customer/', "Customer Dashboard"),
        ('/accounts/profile/', "Profile Settings"),
    ]

    for url, name in customer_urls:
        res = client.get(url)
        assert res.status_code == 200, f"Failed on {name} ({url}): HTTP {res.status_code}"
        print(f"  ✓ [200 OK] Customer: {name} ({url})")

    # Owner Authenticated Tests
    owner = User.objects.get(username='owner_spicedhaba')
    client.force_login(owner)

    owner_urls = [
        ('/dashboard/owner/', "Restaurant Owner Kitchen Dashboard"),
        ('/restaurants/owner/manage-profile/', "Owner Outlet Settings"),
        ('/surplus-food/owner/manage/', "Owner Surplus Food Management"),
        ('/owner/food/add/', "Owner Add Food Item Form"),
    ]

    for url, name in owner_urls:
        res = client.get(url)
        assert res.status_code == 200, f"Failed on {name} ({url}): HTTP {res.status_code}"
        print(f"  ✓ [200 OK] Owner: {name} ({url})")

    # Admin Authenticated Tests
    admin = User.objects.get(username='admin')
    client.force_login(admin)

    admin_urls = [
        ('/dashboard/admin-panel/', "Central Admin Analytics Dashboard with Chart.js"),
    ]

    for url, name in admin_urls:
        res = client.get(url)
        assert res.status_code == 200, f"Failed on {name} ({url}): HTTP {res.status_code}"
        print(f"  ✓ [200 OK] Admin: {name} ({url})")

    print("\n✅ ALL 18 ENDPOINTS PASSED WITH 200 OK! Zero errors detected.")

if __name__ == '__main__':
    run_tests()

