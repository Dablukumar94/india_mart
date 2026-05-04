from django.urls import path

from .views import (BuyNowView, ReturnOrderView,
                    CheckoutView, OrderSuccessView,
                    CancelOrderView, InvoiceView,
                    OrderDetailView, OrderHistoryView)

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', OrderHistoryView.as_view(), name='order-history'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('buy-now/<uuid:pk>/', BuyNowView.as_view(), name='buy-now'),
    path('success/<uuid:order_id>/', OrderSuccessView.as_view(), name='order-success'),
    path('cancel/<uuid:order_id>/', CancelOrderView.as_view(), name='cancel-order'),
    path('return/<uuid:order_id>/', ReturnOrderView.as_view(), name='return-order'),
    path("invoice/<uuid:order_id>/", InvoiceView.as_view(), name="invoice"),
]
