from django.urls import path

from .views import BuyNowView, CheckoutView, OrderDetailView, OrderHistoryView, OrderSuccessView

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('success/', OrderSuccessView.as_view(), name='order-success'),
    path('', OrderHistoryView.as_view(), name='order-history'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('buy-now/<uuid:pk>/', BuyNowView.as_view(), name='buy-now'),
]
