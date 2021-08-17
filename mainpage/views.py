from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('logged_home.html')

    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, 'Account is created for ' + username)

                return redirect('login')

        context = {'form':form}

        return render(request, 'signup.html', context)

def loginPage(request):
    context = {}

    if request.user.is_authenticated:
        return redirect('logged_home.html')

    
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('logged_home.html')
            else:
                messages.info(request, 'Username OR password is incorrect')
                return render(request, 'login.html', context)

    

    return render(request, 'login.html', context)

@login_required(login_url='login')
def logged_home(request):
    return render(request, 'logged_home.html')

def logoutUser(request):
    logout(request)
    return redirect('login')