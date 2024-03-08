from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm,RegisterForm

# https://www.pythontutorial.net/django-tutorial/django-registration/
def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})    
   
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower() # make the user name lowercase before saving it in the database
            user.save()
            messages.success(request, 'You have registered successfully.')
            login(request, user)
            return redirect('manager_home')
        else:
            return render(request, 'register.html', {'form': form})

def sign_in(request):

    if request.method == 'GET':
        form = LoginForm()
        return render(request,'login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                return redirect('manager_home') #succeess page: here must be redirect, not return
        
        # form is not valid or user is not authenticated
        messages.error(request,f' Invalid username or password')
        return render(request,'login.html',{'form': form})
    
def sign_out(request):
    logout(request)
    messages.success(request,f' You have been logged out.')
    return redirect('login')    