from django.urls import path
from . import views

urlpatterns = [
    # ---- Home Page ---- #
    path('', views.home, name='home'),
    path('about/',views.about, name='about'),

    # ---- User Registration & Login ---- #
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # ---- Admin Dashboard ---- #
    path('admin_register/', views.admin_register, name='admin_register'),

    # ---- Food Management ---- #
    path('add_food_item/', views.add_food_item, name='add_food_item'),
    path('food_item_list/', views.food_item_list, name='food_item_list'),
    path('food-list/', views.food_list, name='food_list'),  # Ensure this exists
    path('add-food/', views.add_food_item, name='add_food_item'),
    path('food-items/edit/', views.edit_food_item, name='edit_food_item'),
    path('food-items/delete/', views.delete_food_item, name='delete_food_item'),

    # Cart management
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    #table booking
    path('book-table/', views.book_table, name='book_table'),
    path('table-list/', views.table_list, name='table_list'),
    path('cancel-table/<int:booking_id>/', views.cancel_table, name='cancel_table'),
    path('admin-bookings/', views.admin_bookings, name='admin_bookings'),
]
