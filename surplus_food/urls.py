from django.urls import path
from . import views

app_name = 'surplus_food'

urlpatterns = [
    path('', views.surplus_list, name='surplus_list'),
    path('book/<int:pk>/', views.book_surplus, name='book_surplus'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('owner/manage/', views.owner_surplus_manage, name='owner_surplus_manage'),
    path('owner/booking/<int:booking_id>/pickup/', views.owner_mark_pickup, name='owner_mark_pickup'),
]

