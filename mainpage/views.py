from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

# Create your views here.
def index(request):
    return render(request, 'index.html')

def signup(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'form':form}

    return render(request, 'signup.html', context)

def login(request):
    context = {}

    return render(request, 'login.html', context)

