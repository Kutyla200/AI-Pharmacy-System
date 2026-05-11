from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('dashboard')
        
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # create user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'register.html')

@login_required
def profile(request):

    user = request.user

    if request.method == "POST":

        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')

        user.save()

        messages.success(request, "Profile updated successfully!")

    return render(request, 'profile.html', {'user': user})


def home(request):
    return render(request, "home.html")