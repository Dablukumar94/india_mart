from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order
from .models import Payment


class PaymentDetailView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "amount": order.total_amount,
                "status": "PENDING"
            }
        )

        return render(request, "payments/pay.html", {
            "payment": payment
        })


class ProcessPaymentView(View):
    def post(self, request, pk):
        payment = get_object_or_404(Payment, id=pk)

        method = request.POST.get('method')

        # 🔥 basic validation (important improvement)
        if not method:
            return redirect('payment-detail', order_id=payment.order.id)

        payment.method = method
        payment.status = "SUCCESS"   # (dummy payment logic)
        payment.save()

        order = payment.order
        order.status = "PLACED"
        order.save()

        # 🔥 IMPORTANT FIX (NoReverseMatch safe)
        return redirect('order-success', order_id=order.id)