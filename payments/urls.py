from django.urls import path
from .views import PaymentDetailView, ProcessPaymentView

urlpatterns = [
    path('pay/', PaymentDetailView.as_view(), name='payment-detail'),   # 🔥 NEW
    path('process/', ProcessPaymentView.as_view(), name='process-payment')
]
