from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import FitnessClass, Booking, Profile  # Added Profile

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
    list_display = ('user', 'fitness_class', 'created', 'attended', 'cancelled')  # Changed booking_date to created
    list_filter = ('created', 'fitness_class', 'attended', 'cancelled')  # Changed booking_date to created
    search_fields = ('user__username', 'fitness_class__name')
    date_hierarchy = 'created'  # Changed booking_date to created
    raw_id_fields = ('user', 'fitness_class')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing booking
            return ('user', 'fitness_class', 'created')  # Changed booking_date to created
        return ()

# Register models
admin.site.register(FitnessClass, FitnessClassAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Profile)  # Register the Profile model

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    date_hierarchy = 'date_joined'

# Unregister and re-register User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class BookingAdmin(admin.ModelAdmin):
    # ...
    def booking_date(self, obj):
        return obj.created.date()
    booking_date.short_description = 'Booking Date'
    booking_date.admin_order_field = 'created'
    
    list_display = ('user', 'fitness_class', 'booking_date', 'attended', 'cancelled')