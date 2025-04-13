from django.contrib import admin
from .models import FoodItem, Cart, CartItem,TableBooking

# Check if FoodItem is already registered
if not admin.site.is_registered(FoodItem):
    admin.site.register(FoodItem)

admin.site.register(Cart)
admin.site.register(CartItem)
@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'time', 'seats')
    list_filter = ('date', 'time')
    search_fields = ('user__username', 'date')

