from django import forms
from .models import Product, customer_review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'image', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CustomerReviewForm(forms.ModelForm):
    class Meta:
        model = customer_review
        
        fields = ['message', 'rating']  # Exclude customer_name and date
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.HiddenInput()  # We'll use JS stars, not the default dropdown
        }