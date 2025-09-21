from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StagingReview


class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class ReviewForm(forms.ModelForm):
    class Meta:
        model = StagingReview
        fields = ['translated_review', 'rating']
        widgets = {
            'translated_review': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review...'}),
            'rating': forms.HiddenInput(),  # rating will be handled by stars JS
        }