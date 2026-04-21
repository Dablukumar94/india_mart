from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.

# messages.success(request, "Data saved successfully!")
# messages.error(request, "Something went wrong!")
# messages.warning(request, "Please check your form!")
# messages.info(request, "Welcome back!")

def index_page(request):
    messages.success(request, "Data saved successfully!")
    return render(request, "base/base.html")