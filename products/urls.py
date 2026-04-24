from django.urls import path
from .views import ProductListView, ProductDetailView, AddToCartView, CartView,\
    IncreaseQtyView, DecreaseQtyView, RemoveFromCartView, CheckoutView, \
    OrderSuccessView, OrderHistoryView, OrderDetailView

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/<uuid:pk>/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/', CartView.as_view(), name='cart'),
    path('increase/<uuid:pk>/', IncreaseQtyView.as_view(), name='increase-qty'),
    path('decrease/<uuid:pk>/', DecreaseQtyView.as_view(), name='decrease-qty'),
    path('remove/<uuid:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('success/', OrderSuccessView.as_view(), name='order-success'),
    path('orders/', OrderHistoryView.as_view(), name='order-history'),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
]