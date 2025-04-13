from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from cozy_table.models import FoodItem, UserProfile
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib.auth import login as auth_login
# ---- HOME PAGE ---- #
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def dashboard(request):
    return render(request, 'admin.html')

def register(request):
    return render(request, 'register.html')

def login_view(request):
    return render(request, 'login.html')

def view_cart(request):
    return render(request, 'cart.html')

# ---- USER REGISTRATION & LOGIN ---- #
from .forms import RegistrationForm, OTPVerificationForm
from .models import UserProfile
def register(request):
    """Handles user registration"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            user_profile = UserProfile.objects.create(user=user, phone=phone)
            user_profile.generate_otp()

            # Send OTP email
            send_mail(
                "Your OTP Verification Code",
                f"Your OTP code is {user_profile.otp}",
                "your_email@gmail.com",
                [email],
                fail_silently=False,
            )
            request.session['user_id'] = user.id
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('verify_otp')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

from .models import UserProfile
from .forms import OTPVerificationForm

def verify_otp(request):
    """Handles OTP verification"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')

    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, "User not found. Please register again.")
        return redirect('register')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']

            if entered_otp == user_profile.otp:
                user_profile.is_verified = True
                user_profile.otp = None  # Clear OTP after verification
                user_profile.save()
                
                auth_login(request, user)  # ✅ Corrected login function
                
                request.session.pop('user_id', None)  # ✅ Fix: Avoid KeyError
                messages.success(request, "Account verified! Welcome to your dashboard.")
                return redirect('food_item_list')
            else:
                messages.error(request, "Invalid OTP. Try again.")
    
    else:
        form = OTPVerificationForm()

    return render(request, 'verify_otp.html', {'form': form})


# login for both admin and user
def login(request):

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('/admin/' if user.is_superuser else 'food_item_list')
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# Admin dashboard
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from cozy_table.forms import AdminRegistrationForm, RegistrationForm

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin account created successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Error creating admin account. Please check the form.")

    else:
        form = AdminRegistrationForm()

    return render(request, 'admin_register.html', {'form': form})


# ---- FOOD ITEM MANAGEMENT ---- #

@login_required
def food_item_list(request):
    food_items = FoodItem.objects.all()  # Fetch all food items
    return render(request, 'food_item_list.html', {'food_items': food_items})


from cozy_table.models import FoodItem
from cozy_table.forms import FoodItemForm  # Create a form for FoodItem

@login_required
def add_food_item(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Food item added successfully!")
            return redirect('food_item_list')  # Redirect to the food list page
        else:
            messages.error(request, "Error adding food item. Please check the form.")
    else:
        form = FoodItemForm()

    return render(request, 'add_food_item.html', {'form': form})

@login_required
def food_list(request):
    food_items = FoodItem.objects.all()
    return render(request, 'food_item_list.html', {'food_items': food_items})


@login_required
def edit_food_item(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, instance=food_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Food item updated successfully!")
            return redirect('food_item_list')
        else:
            messages.error(request, "Error updating food item. Please check the form.")
    else:
        form = FoodItemForm(instance=food_item)
    return render(request, 'edit_food_item.html', {'form': form, 'food_item': food_item})

@login_required
def delete_food_item(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)
    if request.method == 'POST':
        food_item.delete()
        messages.success(request, "Food item deleted successfully!")
        return redirect('food_item_list')
    return render(request, 'confirm_delete.html', {'food_item': food_item})



# ---- CART FUNCTIONALITY ---- #
from cozy_table.models import Cart, FoodItem
@login_required
def add_to_cart(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.add(food_item)
    messages.success(request, f"{food_item.name} added to cart!")
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    food_item = get_object_or_404(FoodItem, id=item_id)
    cart.items.remove(food_item)
    messages.success(request, f"{food_item.name} removed from cart!")
    return redirect('view_cart')

@login_required
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.clear()
    messages.success(request, "Cart cleared successfully!")
    return redirect('view_cart')

from cozy_table.models import TableBooking
from cozy_table.forms import TableBookingForm
from datetime import date

@login_required
def book_table(request):
    if request.method == 'POST':
        form = TableBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.is_booked = True  # ✅ Set this manually
            # Check if the selected date and time are already booked
            existing_booking = TableBooking.objects.filter(
                date=booking.date, time=booking.time
            ).exists()

            if existing_booking:
                messages.error(request, "❌ This time slot is already booked. Please choose another time.")
            else:
                booking.save()
                messages.success(request, "✅ Table booked successfully!")
                return redirect('table_list')
    else:
        form = TableBookingForm()
    
    booked_slots = TableBooking.objects.values_list('date', 'time')  # Get booked date & time
    return render(request, 'book_table.html', {'form': form, 'booked_slots': booked_slots})

@login_required
def table_list(request):
    """Displays the list of tables booked by the user"""
    tables = TableBooking.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'table_list.html', {'tables': tables})

@login_required
def cancel_table(request, booking_id):
    """Allows a user to cancel their table booking"""
    booking = get_object_or_404(TableBooking, id=booking_id, user=request.user)
    booking.delete()
    messages.success(request, "✅ Table booking cancelled successfully!")
    return redirect('table_list')

@login_required
def admin_bookings(request):
    """Admin view to see all bookings"""
    if not request.user.is_superuser:
        messages.error(request, "❌ Access Denied!")
        return redirect('home')
    
    bookings = TableBooking.objects.all().order_by('date', 'time')
    return render(request, 'admin_bookings.html', {'bookings': bookings})             


from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_bookings(request):
    bookings = TableBooking.objects.all().order_by('date', 'time')
    return render(request, 'admin_bookings.html', {'bookings': bookings})


