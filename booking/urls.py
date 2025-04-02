from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'booking'

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    
    # Authentication views
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='booking/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # User-specific views
    path('book/<int:class_id>/', views.book_class, name='book_class'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Profile management
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Admin views (for instructors)
    path('manage-classes/', views.manage_classes, name='manage_classes'),
    path('add-class/', views.add_class, name='add_class'),
    path('edit-class/<int:pk>/', views.edit_class, name='edit_class'),
    path('class-attendance/<int:pk>/', views.class_attendance, name='class_attendance'),
]