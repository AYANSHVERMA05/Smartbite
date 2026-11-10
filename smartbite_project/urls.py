from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('menu.urls')),
    path('accounts/', include('accounts.urls')),
    path('restaurants/', include('restaurants.urls')),
    path('orders/', include('orders.urls')),
    path('budget-planner/', include('budget_planner.urls')),
    path('nutrition/', include('nutrition.urls')),
    path('group-orders/', include('group_orders.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('surplus-food/', include('surplus_food.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
