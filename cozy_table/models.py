from django.db import models
from django.contrib.auth.models import User

# ---- USER PROFILES ---- #
import random

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        """Generates a 6-digit OTP"""
        self.otp = str(random.randint(100000, 999999))
        self.save()


class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('starter', 'Starter'),
        ('main_course', 'Main Course'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='main_course')
    available = models.BooleanField(default=True)  # New field for availability
    image_url = models.URLField(max_length=200, blank=True)  # New field for image URL

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(FoodItem, through='CartItem')

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.food_item.name} in {self.cart.user.username}'s cart"
    

class TableBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    seats = models.PositiveIntegerField()
    is_booked = models.BooleanField(default=False)  # ✅ Default added
    
    def __str__(self):
        return f"Table booked by {self.user.username} on {self.date} at {self.time} for {self.seats} seats."
    


