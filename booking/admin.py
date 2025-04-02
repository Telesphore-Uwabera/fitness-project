# booking/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import FitnessClass, Booking

# Custom admin classes for better display of models

class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'capacity')
    list_filter = ('start_time',)
    search_fields = ('name', 'description')
    date_hierarchy = 'start_time'
    ordering = ('start_time',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'capacity')
        }),
    )

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'fitness_class', 'booking_date')
    list_filter = ('booking_date', 'fitness_class')
    search_fields = ('user__username', 'fitness_class__name')
    date_hierarchy = 'booking_date'
    raw_id_fields = ('user', 'fitness_class')  # For better performance with many users/classes
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing booking
            return ('user', 'fitness_class', 'booking_date')
        return ()

# Register models with their custom admin classes
admin.site.register(FitnessClass, FitnessClassAdmin)
admin.site.register(Booking, BookingAdmin)

# Optional: Customize the User admin if needed
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    date_hierarchy = 'date_joined'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)