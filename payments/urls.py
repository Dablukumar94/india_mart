from django.urls import path
from .views import PaymentDetailView, ProcessPaymentView

urlpatterns = [
    path('pay/<uuid:order_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('process/<int:pk>/', ProcessPaymentView.as_view(), name='process-payment'),
]
