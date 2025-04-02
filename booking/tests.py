import os
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from django.contrib.auth.models import User
from .models import FitnessClass, Booking
from django.core.files.uploadedfile import SimpleUploadedFile

class FitnessClassModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified data for all test methods
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='user@example.com'
        )
        
        cls.fitness_class = FitnessClass.objects.create(
            name='Morning Yoga',
            description='Gentle morning yoga session',
            instructor='Jane Doe',
            class_type='yoga',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=15.00,
            location='Studio 1'
        )
        
        # Test image for image field
        cls.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'rb').read(),
            content_type='image/jpeg'
        )

    def test_fitness_class_creation(self):
        self.assertEqual(self.fitness_class.name, 'Morning Yoga')
        self.assertEqual(self.fitness_class.instructor, 'Jane Doe')
        self.assertEqual(self.fitness_class.class_type, 'yoga')
        self.assertEqual(self.fitness_class.spots_remaining, 10)
        self.assertTrue(self.fitness_class.is_upcoming())
        
    def test_image_upload(self):
        fitness_class = FitnessClass.objects.create(
            name='Pilates Class',
            description='Pilates session',
            instructor='John Smith',
            class_type='pilates',
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=1),
            capacity=8,
            image=self.test_image
        )
        self.assertTrue(fitness_class.image.name.startswith('class_images/'))
        
    def test_duration_property(self):
        self.assertEqual(self.fitness_class.duration, 60)
        
    def test_spots_remaining(self):
        # Create 3 bookings
        for i in range(3):
            Booking.objects.create(
                user=self.user,
                fitness_class=self.fitness_class
            )
        self.assertEqual(self.fitness_class.spots_remaining, 7)
        
    def test_is_full(self):
        # Fill all spots
        for i in range(10):
            Booking.objects.create(
                user=User.objects.create_user(
                    username=f'testuser{i}',
                    password='testpass123'
                ),
                fitness_class=self.fitness_class
            )
        self.assertTrue(self.fitness_class.is_full())
        
    def test_string_representation(self):
        self.assertEqual(
            str(self.fitness_class),
            f"Morning Yoga with Jane Doe at {self.fitness_class.start_time.strftime('%Y-%m-%d %H:%M')}"
        )

class BookingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='user@example.com'
        )
        
        cls.fitness_class = FitnessClass.objects.create(
            name='Evening HIIT',
            description='High intensity interval training',
            instructor='Mike Johnson',
            class_type='hiit',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            capacity=15
        )
        
        cls.booking = Booking.objects.create(
            user=cls.user,
            fitness_class=cls.fitness_class
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.user.username, 'testuser')
        self.assertEqual(self.booking.fitness_class.name, 'Evening HIIT')
        self.assertFalse(self.booking.attended)
        self.assertFalse(self.booking.cancelled)
        
    def test_confirmation_email_sent(self):
        # Test that email was sent on creation
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Booking Confirmation: Evening HIIT')
        
    def test_cancellation_email(self):
        self.booking.cancel(reason="Change of plans")
        self.assertEqual(len(mail.outbox), 2)  # Confirmation + cancellation
        self.assertEqual(mail.outbox[1].subject, 'Booking Cancelled: Evening HIIT')
        self.assertTrue(self.booking.cancelled)
        
    def test_unique_together_constraint(self):
        # Try to create duplicate booking
        with self.assertRaises(Exception):
            Booking.objects.create(
                user=self.user,
                fitness_class=self.fitness_class
            )

class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        cls.fitness_class = FitnessClass.objects.create(
            name='Power Cycling',
            description='Intense cycling class',
            instructor='Sarah Connor',
            class_type='cycling',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            capacity=20
        )
        
        cls.client = Client()
        
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Power Cycling')
        
    def test_class_detail_view(self):
        url = reverse('class_detail', args=[self.fitness_class.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sarah Connor')
        
    def test_book_class_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('book_class', args=[self.fitness_class.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after booking
        self.assertEqual(Booking.objects.count(), 1)
        
    def test_book_class_view_unauthenticated(self):
        url = reverse('book_class', args=[self.fitness_class.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(Booking.objects.count(), 0)
        
    def test_my_bookings_view(self):
        # Create a booking first
        Booking.objects.create(
            user=self.user,
            fitness_class=self.fitness_class
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Power Cycling')
        
    def test_register_view(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': 'newuser',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

class BusinessLogicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a class that's already happened
        cls.past_class = FitnessClass.objects.create(
            name='Past Class',
            description='This class already happened',
            instructor='Old Instructor',
            class_type='yoga',
            start_time=timezone.now() - timedelta(days=1),
            end_time=timezone.now() - timedelta(days=1, hours=1),
            capacity=5
        )
        
        # Create a full class
        cls.full_class = FitnessClass.objects.create(
            name='Full Class',
            description='This class is full',
            instructor='Popular Instructor',
            class_type='pilates',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            capacity=2
        )
        # Book all spots
        for i in range(2):
            user = User.objects.create_user(
                username=f'user{i}',
                password='testpass123'
            )
            Booking.objects.create(
                user=user,
                fitness_class=cls.full_class
            )
    
    def test_cannot_book_past_class(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('book_class', args=[self.past_class.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)  # Bad request
        self.assertEqual(Booking.objects.filter(fitness_class=self.past_class).count(), 0)
        
    def test_cannot_book_full_class(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('book_class', args=[self.full_class.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)  # Bad request
        self.assertEqual(Booking.objects.filter(fitness_class=self.full_class).count(), 2)
        
    def test_cancel_booking(self):
        # Create a booking to cancel
        booking = Booking.objects.create(
            user=self.user,
            fitness_class=FitnessClass.objects.create(
                name='Cancel Test',
                description='Test cancellation',
                instructor='Test Instructor',
                class_type='dance',
                start_time=timezone.now() + timedelta(days=2),
                end_time=timezone.now() + timedelta(days=2, hours=1),
                capacity=10
            )
        )
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('cancel_booking', args=[booking.id])
        response = self.client.post(url, {
            'reason': 'Change of plans'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after cancellation
        booking.refresh_from_db()
        self.assertTrue(booking.cancelled)
        self.assertEqual(booking.cancellation_reason, 'Change of plans')