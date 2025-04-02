from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import FitnessClass, Booking
from .forms import FitnessClassForm, ProfileForm

def home(request):
    """Display all upcoming fitness classes"""
    now = timezone.now()
    classes = FitnessClass.objects.filter(
        start_time__gte=now,
        is_active=True
    ).order_by('start_time')
    return render(request, 'booking/home.html', {'classes': classes})

def class_detail(request, pk):
    """Show details for a specific fitness class"""
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    is_booked = False
    if request.user.is_authenticated:
        is_booked = Booking.objects.filter(
            user=request.user,
            fitness_class=fitness_class,
            cancelled=False
        ).exists()
    return render(request, 'booking/class_detail.html', {
        'fitness_class': fitness_class,
        'is_booked': is_booked,
        'spots_remaining': fitness_class.spots_remaining
    })

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'booking/register.html', {'form': form})

@login_required
def book_class(request, class_id):
    """Handle class bookings"""
    fitness_class = get_object_or_404(FitnessClass, pk=class_id)
    
    # Validate the booking
    if fitness_class.start_time < timezone.now():
        messages.error(request, 'Cannot book a class that has already occurred.')
        return redirect('class_detail', pk=class_id)
    
    if fitness_class.is_full():
        messages.error(request, 'This class is already full.')
        return redirect('class_detail', pk=class_id)
    
    if Booking.objects.filter(user=request.user, fitness_class=fitness_class).exists():
        messages.warning(request, 'You have already booked this class!')
        return redirect('my_bookings')
    
    # Create the booking
    Booking.objects.create(user=request.user, fitness_class=fitness_class)
    messages.success(request, f'Successfully booked {fitness_class.name}!')
    return redirect('my_bookings')

@login_required
def my_bookings(request):
    """Show user's upcoming bookings"""
    bookings = Booking.objects.filter(
        user=request.user,
        cancelled=False,
        fitness_class__start_time__gte=timezone.now()
    ).select_related('fitness_class').order_by('fitness_class__start_time')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    """Handle booking cancellations"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        booking.cancel(reason=reason)
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('my_bookings')
    
    return render(request, 'booking/cancel_booking.html', {'booking': booking})

@login_required
def profile(request):
    """Display user profile"""
    return render(request, 'booking/profile.html', {'user': request.user})

@login_required
def update_profile(request):
    """Update user profile information"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'booking/update_profile.html', {'form': form})

# Instructor/admin views
@login_required
def manage_classes(request):
    """View for instructors to manage their classes"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    now = timezone.now()
    upcoming_classes = FitnessClass.objects.filter(
        instructor=request.user.get_full_name() or request.user.username,
        start_time__gte=now
    ).order_by('start_time')
    
    past_classes = FitnessClass.objects.filter(
        instructor=request.user.get_full_name() or request.user.username,
        start_time__lt=now
    ).order_by('-start_time')
    
    return render(request, 'booking/manage_classes.html', {
        'upcoming_classes': upcoming_classes,
        'past_classes': past_classes
    })

@login_required
def add_class(request):
    """Add a new fitness class"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = FitnessClassForm(request.POST, request.FILES)
        if form.is_valid():
            fitness_class = form.save(commit=False)
            fitness_class.instructor = request.user.get_full_name() or request.user.username
            fitness_class.save()
            messages.success(request, 'Class added successfully!')
            return redirect('manage_classes')
    else:
        form = FitnessClassForm()
    
    return render(request, 'booking/add_class.html', {'form': form})

@login_required
def edit_class(request, pk):
    """Edit an existing fitness class"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    
    if request.method == 'POST':
        form = FitnessClassForm(request.POST, request.FILES, instance=fitness_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('manage_classes')
    else:
        form = FitnessClassForm(instance=fitness_class)
    
    return render(request, 'booking/edit_class.html', {'form': form, 'fitness_class': fitness_class})

@login_required
def class_attendance(request, pk):
    """View and manage class attendance"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    bookings = Booking.objects.filter(
        fitness_class=fitness_class,
        cancelled=False
    ).select_related('user')
    
    if request.method == 'POST':
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