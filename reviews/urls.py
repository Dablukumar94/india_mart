# reviews/urls.py

from django.urls import path
from .views import AddReviewView

urlpatterns = [
    path("add/", AddReviewView.as_view(), name="add-review"),
]