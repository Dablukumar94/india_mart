from django.urls import path
from .views import SignupView, LoginView, LogoutView, AddressView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('address/', AddressView.as_view(), name='address'),
]