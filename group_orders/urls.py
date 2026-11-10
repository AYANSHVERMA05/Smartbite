from django.urls import path
from . import views

app_name = 'group_orders'

urlpatterns = [
    path('', views.group_order_list, name='group_order_list'),
    path('create/', views.create_group_order, name='create_group_order'),
    path('join/', views.join_group_order, name='join_group_order'),
    path('order/<str:group_code>/', views.group_order_detail, name='group_order_detail'),
    path('order/<str:group_code>/add/', views.add_item_to_group, name='add_item_to_group'),
    path('item/<int:item_id>/remove/', views.remove_group_item, name='remove_group_item'),
    path('order/<str:group_code>/checkout/', views.checkout_group_order, name='checkout_group_order'),
]

