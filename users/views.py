from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from . import forms
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password = data['password']) #returns a user object
            print(data)

            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                return HttpResponse("Invalid Login")

    else:
        form = forms.LoginForm()
    return render(request,'users/login.html',{'form':form})

def sign_up(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request,user)
            return redirect('home')
        else:
            print(form.errors)
            return HttpResponse('invalid form')
        
    else:
        form = forms.RegisterForm()
        return render(request, 'users/register.html',{'form':form})

def base(request):
    return render(request, 'users/base.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('base')

