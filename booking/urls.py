from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

app_name = 'booking'

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    
    # Enhanced authentication views
    path('register/', views.register, name='register'),
    path('login/', 
         auth_views.LoginView.as_view(
             template_name='booking/login.html',
             authentication_form=AuthenticationForm,
             extra_context={
                 'next': '/',  # Default redirect after login
                 'title': 'Member Login'
             }
         ), 
         name='login'),
    path('logout/', 
         auth_views.LogoutView.as_view(
             template_name='booking/logged_out.html',
             next_page='booking:home'
         ), 
         name='logout'),
    
    # Password reset flows
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='booking/password_reset.html',
             email_template_name='booking/password_reset_email.html',
             subject_template_name='booking/password_reset_subject.txt',
             success_url='done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='booking/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='booking/password_reset_confirm.html',
             success_url='/password-reset/complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='booking/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # User-specific views
    path('book/<int:class_id>/', views.book_class, name='book_class'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Profile management
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Admin views
    path('manage-classes/', views.manage_classes, name='manage_classes'),
    path('add-class/', views.add_class, name='add_class'),
    path('edit-class/<int:pk>/', views.edit_class, name='edit_class'),
    path('class-attendance/<int:pk>/', views.class_attendance, name='class_attendance'),
    
    # Additional auth-related
    path('account-inactive/', views.account_inactive, name='account_inactive'),
    path('admin/', admin.site.urls),
    
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
     path('login/', 
         auth_views.LoginView.as_view(
             template_name='registration/login.html',
             extra_context={
                 'title': 'Member Login'
             }
         ), 
         name='login'),
]