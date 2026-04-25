from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


# 🔐 Signup
class SignupView(View):

    def get(self, request):
        return render(request, "accounts/signup.html")

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 🔥 Password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        # 🔥 Email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect('signup')

        # 🔥 Create user
        User.objects.create_user(
            username=email,   # email as username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "Account created successfully!")
        return redirect('login')


# 🔐 Login
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
        # messages.success(request, "Login successful!")

        # 🔥 next redirect (important)
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)

        return redirect('product-list')

# 🚪 Logout
class LogoutView(View):

    def post(self, request):
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('product-list')


    def get(self, request):  # fallback
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('login')
        