from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomerProfile

User = get_user_model()


class UserRegisterForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Student / Customer'),
        ('RESTAURANT_OWNER', 'Restaurant / Canteen Owner'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}))
    
    # Optional fields for student/customer profile
    hostel_block_room = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Block B, Room 204'}))
    preferred_diet = forms.ChoiceField(choices=CustomerProfile.DIET_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    # Optional fields for restaurant owner
    restaurant_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of your Restaurant / Stall'}))
    restaurant_address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campus Food Court, Booth #3'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@university.edu'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        role = cleaned_data.get('role')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match!")

        if role == 'RESTAURANT_OWNER':
            if not cleaned_data.get('restaurant_name'):
                self.add_error('restaurant_name', 'Restaurant Name is required for restaurant owners.')

        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomerProfile
        fields = ['delivery_address', 'hostel_block_room', 'preferred_diet', 'daily_budget_limit']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Delivery address / landmark'}),
            'hostel_block_room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Block B, Room 204'}),
            'preferred_diet': forms.Select(attrs={'class': 'form-select'}),
            'daily_budget_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '10'}),
        }

