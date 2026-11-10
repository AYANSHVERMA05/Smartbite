from django import forms
from .models import FoodItem, Review, FoodCategory


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'category', 'description', 'price', 'meal_type', 'is_veg', 'is_available', 'preparation_time', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Paneer Butter Masala'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe taste, ingredients and portion size'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1.00', 'placeholder': '120.00'}),
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'is_veg': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/food.jpg'}),
        }


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(5, '★★★★★ (5 - Excellent)'), (4, '★★★★☆ (4 - Very Good)'), (3, '★★★☆☆ (3 - Average)'), (2, '★★☆☆☆ (2 - Below Average)'), (1, '★☆☆☆☆ (1 - Poor)')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience with taste, portion and packaging...'}),
        }

