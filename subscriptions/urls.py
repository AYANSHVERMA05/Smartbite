from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.plan_list, name='plan_list'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    path('cancel/<int:sub_id>/', views.cancel_subscription, name='cancel_subscription'),
]

