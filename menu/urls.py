from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.food_list, name='food_list'),
    path('food/<int:pk>/', views.food_detail, name='food_detail'),
    path('owner/food/add/', views.add_food_item, name='add_food_item'),
    path('owner/food/<int:pk>/edit/', views.edit_food_item, name='edit_food_item'),
    path('owner/food/<int:pk>/delete/', views.delete_food_item, name='delete_food_item'),
    path('owner/food/<int:pk>/toggle/', views.toggle_food_availability, name='toggle_food_availability'),
]

