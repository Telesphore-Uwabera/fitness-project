from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, FitnessClass

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    birth_date = forms.DateField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "phone_number", "birth_date")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class FitnessClassForm(forms.ModelForm):
    class Meta:
        model = FitnessClass
        fields = '__all__'
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'birth_date', 'emergency_contact', 
                 'emergency_phone', 'health_notes', 'profile_picture']