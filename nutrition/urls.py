from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('filter/', views.nutrition_filter_view, name='food_nutrition_filter'),
]

