from django.urls import path
from . import views

app_name = 'budget_planner'

urlpatterns = [
    path('', views.budget_planner_view, name='planner'),
    path('add-combo/', views.add_combo_to_cart, name='add_combo_to_cart'),
]

