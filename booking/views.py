from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from datetime import timedelta
from .models import FitnessClass, Booking, Profile
from .forms import FitnessClassForm, ProfileForm, CustomUserCreationForm
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
import os
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect

def home(request):
    """Display all upcoming fitness classes with filtering options"""
    now = timezone.now()
    query = request.GET.get('q')
    class_type = request.GET.get('type')
    
    classes = FitnessClass.objects.filter(
        start_time__gte=now,
        is_active=True
    ).order_by('start_time')
    
    if query:
        classes = classes.filter(
            Q(name__icontains=query) | 
            Q(instructor__icontains=query) |
            Q(description__icontains=query)
        )
    
    if class_type:
        classes = classes.filter(class_type=class_type)
    
    # Get popular classes (most bookings)
    popular_classes = FitnessClass.objects.filter(
        start_time__gte=now,
        is_active=True
    ).annotate(
        num_bookings=Count('bookings')
    ).order_by('-num_bookings')[:3]
    
    return render(request, 'booking/home.html', {
        'classes': classes,
        'popular_classes': popular_classes,
        'class_types': FitnessClass.CLASS_TYPES,
        'search_query': query,
        'selected_type': class_type
    })

def class_detail(request, pk):
    """Show details for a specific fitness class with related classes"""
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    is_booked = False
    user_has_booking = False
    
    if request.user.is_authenticated:
        is_booked = Booking.objects.filter(
            user=request.user,
            fitness_class=fitness_class,
            cancelled=False
        ).exists()
        
        # Check if user has any booking for this class (including cancelled)
        user_has_booking = Booking.objects.filter(
            user=request.user,
            fitness_class=fitness_class
        ).exists()
    
    # Get similar classes (same type)
    similar_classes = FitnessClass.objects.filter(
        class_type=fitness_class.class_type,
        start_time__gte=timezone.now(),
        is_active=True
    ).exclude(pk=pk).order_by('start_time')[:3]
    
    return render(request, 'booking/class_detail.html', {
        'fitness_class': fitness_class,
        'is_booked': is_booked,
        'user_has_booking': user_has_booking,
        'spots_remaining': fitness_class.spots_remaining,
        'similar_classes': similar_classes
    })

def register(request):
    """Handle user registration with profile creation"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create profile for the user
            Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data.get('phone_number'),
                birth_date=form.cleaned_data.get('birth_date')
            )
            
            # Fix authentication backend
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            messages.success(request, 'Registration successful!')
            return redirect('home')  # Ensure this matches your URL pattern
    else:
        form = CustomUserCreationForm()
    return render(request, 'booking/register.html', {'form': form})

def home(request):
    """Simple home page view"""
    return render(request, 'booking/home.html')

@login_required
def book_class(request, class_id):
    """Handle class bookings with waitlist functionality"""
    fitness_class = get_object_or_404(FitnessClass, pk=class_id)
    
    # Validate the booking
    if fitness_class.start_time < timezone.now():
        messages.error(request, 'Cannot book a class that has already occurred.')
        return redirect('class_detail', pk=class_id)
    
    if fitness_class.is_full():
        messages.warning(request, 'This class is full, but you have been added to the waitlist.')
        # Implement waitlist logic here
        return redirect('class_detail', pk=class_id)
    
    existing_booking = Booking.objects.filter(
        user=request.user,
        fitness_class=fitness_class
    ).first()
    
    if existing_booking:
        if existing_booking.cancelled:
            existing_booking.cancelled = False
            existing_booking.save()
            messages.success(request, 'Your previously cancelled booking has been reinstated!')
        else:
            messages.warning(request, 'You have already booked this class!')
        return redirect('my_bookings')
    
    # Create the booking
    Booking.objects.create(user=request.user, fitness_class=fitness_class)
    messages.success(request, f'Successfully booked {fitness_class.name}!')
    
    # Send confirmation email (implement email functionality)
    # send_booking_confirmation(request.user, fitness_class)
    
    return redirect('my_bookings')

@login_required
def my_bookings(request):
    """Show user's upcoming bookings with cancellation deadlines"""
    now = timezone.now()
    bookings = Booking.objects.filter(
        user=request.user,
        cancelled=False,
        fitness_class__start_time__gte=now
    ).select_related('fitness_class').order_by('fitness_class__start_time')
    
    # Calculate cancellation deadlines (24 hours before class)
    for booking in bookings:
        booking.cancellation_deadline = booking.fitness_class.start_time - timedelta(hours=24)
        booking.can_cancel = now < booking.cancellation_deadline
    
    past_bookings = Booking.objects.filter(
        user=request.user,
        fitness_class__start_time__lt=now
    ).select_related('fitness_class').order_by('-fitness_class__start_time')[:10]
    
    return render(request, 'booking/my_bookings.html', {
        'bookings': bookings,
        'past_bookings': past_bookings
    })

@login_required
def cancel_booking(request, booking_id):
    """Handle booking cancellations with deadlines"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    cancellation_deadline = booking.fitness_class.start_time - timedelta(hours=24)
    
    if timezone.now() > cancellation_deadline:
        messages.error(request, 'Cancellation deadline has passed (24 hours before class).')
        return redirect('my_bookings')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        booking.cancel(reason=reason)
        messages.success(request, 'Booking cancelled successfully.')
        
        # Send cancellation email (implement email functionality)
        # send_cancellation_notification(request.user, booking.fitness_class, reason)
        
        return redirect('my_bookings')
    
    return render(request, 'booking/cancel_booking.html', {
        'booking': booking,
        'cancellation_deadline': cancellation_deadline
    })

@login_required
def profile(request):
    """Display user profile with booking statistics"""
    user = request.user
    now = timezone.now()
    
    # Get booking stats
    total_bookings = Booking.objects.filter(user=user).count()
    upcoming_bookings = Booking.objects.filter(
        user=user,
        cancelled=False,
        fitness_class__start_time__gte=now
    ).count()
    attended_classes = Booking.objects.filter(
        user=user,
        attended=True
    ).count()
    
    # Get recently attended classes
    recent_classes = Booking.objects.filter(
        user=user,
        attended=True
    ).select_related('fitness_class').order_by('-fitness_class__start_time')[:5]
    
    return render(request, 'booking/profile.html', {
        'user': user,
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming_bookings,
        'attended_classes': attended_classes,
        'recent_classes': recent_classes
    })

@login_required
def update_profile(request):
    """Update user profile information with picture upload"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'booking/update_profile.html', {'form': form})

# Instructor/admin views
@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_classes(request):
    """View for instructors to manage their classes with stats"""
    instructor = request.user.get_full_name() or request.user.username
    now = timezone.now()
    
    upcoming_classes = FitnessClass.objects.filter(
        instructor=instructor,
        start_time__gte=now
    ).annotate(
        num_bookings=Count('bookings', filter=Q(bookings__cancelled=False))
    ).order_by('start_time')
    
    past_classes = FitnessClass.objects.filter(
        instructor=instructor,
        start_time__lt=now
    ).annotate(
        num_attended=Count('bookings', filter=Q(bookings__attended=True))
    ).order_by('-start_time')
    
    # Calculate attendance percentage for past classes
    for cls in past_classes:
        if cls.capacity > 0:
            cls.attendance_percentage = (cls.num_attended / cls.capacity) * 100
        else:
            cls.attendance_percentage = 0
    
    return render(request, 'booking/manage_classes.html', {
        'upcoming_classes': upcoming_classes,
        'past_classes': past_classes
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_class(request):
    """Add a new fitness class with recurring option"""
    if request.method == 'POST':
        form = FitnessClassForm(request.POST, request.FILES)
        if form.is_valid():
            fitness_class = form.save(commit=False)
            fitness_class.instructor = request.user.get_full_name() or request.user.username
            fitness_class.save()
            
            # Handle recurring classes (implement as needed)
            # if form.cleaned_data.get('is_recurring'):
            #     create_recurring_classes(fitness_class)
            
            messages.success(request, 'Class added successfully!')
            return redirect('manage_classes')
    else:
        form = FitnessClassForm()
    
    return render(request, 'booking/add_class.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_class(request, pk):
    """Edit an existing fitness class with validation"""
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    
    if request.method == 'POST':
        form = FitnessClassForm(request.POST, request.FILES, instance=fitness_class)
        if form.is_valid():
            # Prevent changing class time if bookings exist
            if 'start_time' in form.changed_data and fitness_class.bookings.exists():
                messages.error(request, 'Cannot change class time after bookings have been made.')
            else:
                form.save()
                messages.success(request, 'Class updated successfully!')
                return redirect('manage_classes')
    else:
        form = FitnessClassForm(instance=fitness_class)
    
    return render(request, 'booking/edit_class.html', {
        'form': form,
        'fitness_class': fitness_class,
        'has_bookings': fitness_class.bookings.exists()
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def class_attendance(request, pk):
    """View and manage class attendance with export option"""
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    bookings = Booking.objects.filter(
        fitness_class=fitness_class,
        cancelled=False
    ).select_related('user')
    
    if request.method == 'POST':
        if 'export' in request.POST:
            # Implement CSV export functionality
            # return export_attendance_csv(bookings)
            pass
        else:
            # Handle attendance updates
            for booking in bookings:
                attended = request.POST.get(f'attended_{booking.id}') == 'on'
                booking.attended = attended
                booking.save()
            messages.success(request, 'Attendance updated successfully!')
            return redirect('class_attendance', pk=pk)
    
    return render(request, 'booking/class_attendance.html', {
        'fitness_class': fitness_class,
        'bookings': bookings
    })

# AJAX/API endpoints
@login_required
def check_class_availability(request, class_id):
    """JSON endpoint for checking class availability"""
    fitness_class = get_object_or_404(FitnessClass, pk=class_id)
    is_booked = Booking.objects.filter(
        user=request.user,
        fitness_class=fitness_class,
        cancelled=False
    ).exists()
    
    return JsonResponse({
        'available': not fitness_class.is_full(),
        'is_booked': is_booked,
        'spots_remaining': fitness_class.spots_remaining
    })

@login_required
def quick_cancel_booking(request, booking_id):
    """Handle quick cancellation via AJAX"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    cancellation_deadline = booking.fitness_class.start_time - timedelta(hours=24)
    
    if timezone.now() > cancellation_deadline:
        return JsonResponse({'success': False, 'message': 'Cancellation deadline has passed'})
    
    booking.cancel()
    return JsonResponse({'success': True, 'message': 'Booking cancelled'})

# Helper functions
def is_instructor(user):
    return user.is_staff

def account_inactive(request):
    # Your view logic here
    return render(request, 'booking/account_inactive.html')

def terms(request):
    return render(request, 'booking/terms.html')

def privacy(request):
    return render(request, 'booking/privacy.html')
@requires_csrf_token
def csrf_failure(request, reason=""):
    ctx = {
        'reason': reason,
        'codespace_name': os.getenv('CODESPACE_NAME'),
        'admin_url': settings.ADMIN_URL
    }
    return render(request, '403_csrf.html', status=403)

@never_cache
@csrf_protect
def custom_admin_logout(request):
    logout(request)
    return redirect('admin  :login')
def home(request):
    return render(request, 'booking/home.html')
