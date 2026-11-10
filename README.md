# SmartBite — Smart Food Ordering and Management System
**Intermediate-Level B.Tech Academic Project**  
*Built with Python, Django 6.1, SQLite, Bootstrap 5, Scikit-learn, and Chart.js*

---

## 🌟 Project Overview
**SmartBite** is a full-featured campus dining and food ordering system tailored for university environments, hostel students, and campus cafeterias. Rather than being just another generic food clone, SmartBite implements six distinctive, practical modules designed to impress in college project presentations and technical vivas:

1. **Smart Budget Meal Planner**: Partitions any daily food budget limit (e.g. ₹200, ₹350, ₹500) into balanced Breakfast, Lunch, and Dinner combos with remaining savings calculation and one-click cart ordering.
2. **AI Food Recommendations**: Uses Scikit-learn TF-IDF Vectorization and Cosine Similarity to compute dietary matches and suggest items based on past orders with transparent "Why Recommended" explanations.
3. **Food Waste Reduction (Surplus Food)**: Enables restaurant owners to list fresh extra meal batches at 40–60% discounts before pickup deadlines to curb campus food waste.
4. **Group Ordering for Hostels**: Generates unique 6-character alphanumeric invitation codes allowing hostel roommates to assemble individual plates into a single master COD order with per-member contribution calculations.
5. **Hostel Mess Subscriptions**: Weekly (7-day) and monthly (30-day) dining plans for Breakfast, Lunch & Dinner delivered to hostel gates with pause/cancellation capability.
6. **Smart Nutrition & Macro Filtering**: Real-time calorie and protein threshold sliders with vegetarian indicators.
7. **Role-Based Operations & Analytics**: Separate workflows for **Students/Customers**, **Restaurant Owners (Kitchen Queue)**, and **System Administrators (Chart.js visualizations)**.

---

## 🎨 Color Palette & Design
- **Primary Orange**: `#ea580c` / `#f97316` (Food vibrancy & CTAs)
- **Dark Green**: `#14532d` / `#15803d` (Hygiene, vegetarian badges & health metrics)
- **Clean White & Crisp Grays**: `#ffffff` and `#f8fafc` (Modern card layouts)

---

## 🚀 How to Run the Project

### 1. Open Terminal / PowerShell in the Project Root
```powershell
cd C:\Users\ayans\.gemini
```

### 2. Start the Development Server
```powershell
python manage.py runserver
```
*(Alternatively, run `python SESD/main.py`)*

### 3. Open in Your Web Browser
Navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo Login Accounts (Pre-Seeded)

| Role | Username | Password | Features Accessible |
| :--- | :--- | :--- | :--- |
| **Student / Customer** | `rahul` | `student123` | Cart, COD checkout, Budget Planner, Group Ordering, Surplus Booking, AI Recommendations |
| **Student / Customer (Veg)** | `priya` | `student123` | Pure Veg diet profile, nutrition filters, mess subscriptions |
| **Restaurant Owner 1** | `owner_spicedhaba` | `owner123` | Kitchen order queue (status toggle), menu management, surplus food listings |
| **Restaurant Owner 2** | `owner_greenbowl` | `owner123` | Healthy bowls menu, nutrition management, outlet settings |
| **Administrator** | `admin` | `admin123` | Central analytics, Chart.js trends, outlet approvals, Django Admin (`/admin/`) |

---

## 📁 Modular Project Architecture

```
smartbite/
├── accounts/            # Custom User model, CustomerProfile, login, registration, roles
├── restaurants/         # Restaurant profile, outlet listing, menu viewing
├── menu/                # Food categories, food items, reviews, availability toggle
├── orders/              # Cart, CartItem, Order, OrderItem, COD checkout, status tracking
├── budget_planner/      # Daily budget partitioning & scoring logic
├── group_orders/        # Shared carts, 6-character room codes, split bill breakdown
├── recommendations/     # Scikit-learn TF-IDF & Cosine Similarity AI engine
├── surplus_food/        # Food waste reduction, discounted batches, pickup deadlines
├── subscriptions/       # Weekly & monthly hostel mess dining subscriptions
├── nutrition/           # FoodNutrition model, calorie/protein filtering
├── dashboard/           # Customer, Restaurant Kitchen, and Admin Chart.js consoles
├── templates/           # Bootstrap 5 responsive templates
├── static/              # CSS & JavaScript assets
├── seed_data.py         # Complete database seeding script
├── test_suite.py        # Automated test verification for all endpoints
└── manage.py            # Django CLI management
```

---

## 🎓 Academic Viva Questions & Answers

**Q1: How does the AI recommendation engine work?**  
*Answer:* It implements content-based filtering. Discarding black-box complexity, it constructs feature strings from Category, Veg/Non-Veg, Price Tier, and Nutritional Tags. Using `sklearn.feature_extraction.text.TfidfVectorizer` and `sklearn.metrics.pairwise.cosine_similarity`, it compares the candidate food items against the user's past order history. For new users without order history (cold-start problem), it gracefully falls back to popularity-weighted top-rated items matching their diet.

**Q2: What is the algorithmic approach behind the Budget Meal Planner?**  
*Answer:* The planner uses a modular Python combinatorial heuristic. It partitions dishes into Breakfast, Lunch, and Dinner pools within target budget proportions (e.g. ~25% breakfast, ~45% lunch, ~35% dinner), generates valid triples satisfying $Cost(B) + Cost(L) + Cost(D) \le Budget$, and scores each combination based on budget utilization and protein density.

**Q3: How is data consistency maintained during Group Orders?**  
*Answer:* Each group order has a unique alphanumeric invitation code. Individual members add their dishes linked to their `GroupMember` foreign key. The host finalizes the order into a master `Order` record, preserving each item's member attribution while keeping campus COD payment simple and unified.
