from django.urls import path
from .views import (
    AddToCartView,
    CartView,
    IncreaseQtyView,
    DecreaseQtyView,
    RemoveFromCartView
)

urlpatterns = [
    path('add/<uuid:pk>/', AddToCartView.as_view(), name='add-to-cart'),
    path('', CartView.as_view(), name='cart'),
    path('increase/<uuid:pk>/', IncreaseQtyView.as_view(), name='increase-qty'),
    path('decrease/<uuid:pk>/', DecreaseQtyView.as_view(), name='decrease-qty'),
    path('remove/<uuid:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
]