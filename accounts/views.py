from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

class SignupView(View):

    def get(self, request):
        return render(request, "accounts/signup.html")

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully!")
        return redirect('login')

class LoginView(View):

    def get(self, request):
        return render(request, "accounts/login.html")

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect('login')

        login(request, user)
        messages.success(request, "Login successful!")
        return redirect('home')

class LogoutView(View):

    def get(self, request):
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('login')