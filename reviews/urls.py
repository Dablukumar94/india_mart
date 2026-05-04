# reviews/urls.py

from django.urls import path
from .views import AddReviewAjaxView

urlpatterns = [
    path("add-review/", AddReviewAjaxView.as_view(), name="add-review"),
]