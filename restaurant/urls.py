from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('', include('cozy_table.urls')),  # Include your app's URL patterns
    
]