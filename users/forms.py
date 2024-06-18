from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100,label='Username',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Username'}))
    password = forms.CharField(max_length=100,label='Password',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Password'})) #masks all characters

class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password'}))
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password Again'}))
    class Meta:
        model = User
        fields = ['username','email','first_name']
        widgets = {
            'username': forms.TextInput(attrs = {'class':'form-control','placeholder':'Enter Username'}),
            'email': forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter Email'}),
            'first_name': forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Your Name'}),
        }

    def check_password(self):
        if self.cleaned_data['password']!=self.cleaned_data['password2']:
            raise forms.ValidationError('Passwords do not Match')
        return self.cleaned_data['password2']
        