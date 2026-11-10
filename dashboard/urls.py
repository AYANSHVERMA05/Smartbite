from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('owner/', views.owner_dashboard, name='owner_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('restaurant/<int:pk>/toggle/', views.toggle_restaurant_status, name='toggle_restaurant_status'),
]

