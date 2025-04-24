from django import forms
from django.contrib.auth.forms import UserCreationForm

from afms_app.models import Vehicle
from .models import Profile, User
from django.forms.widgets import ClearableFileInput  

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    phone = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}))
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], widget=forms.Select(attrs={'class': 'form-select'}))
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    user_type = forms.ChoiceField(choices=[('buyer', 'Buyer'), ('farm_owner', 'Farm Owner')], widget=forms.Select(attrs={'class': 'form-select'}), required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'gender', 'password1', 'password2', 'user_type']



class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'gender']

    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [ 'full_name', 'country', 'state', 'city', 'address']
        widgets = {
            'image': ClearableFileInput(attrs={'class': 'form-control-file'})
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.input_type != 'file':
                field.widget.attrs['class'] = 'form-control'


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['is_available','state']
        widgets = {
            'is_available': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
        }


