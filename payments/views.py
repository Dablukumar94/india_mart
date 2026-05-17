from django.views import View
from django.shortcuts import render, redirect

from accounts.models import Address
from carts.models import Cart
from .models import Payment

from orders.services import create_order_from_checkout


class PaymentDetailView(View):
    def get(self, request):
        checkout_data = request.session.get("checkout_data")

        if not checkout_data:
            return redirect('cart')

        return render(request, "payments/pay.html", {
            "data": checkout_data
        })


class ProcessPaymentView(View):
    def post(self, request):

        checkout_data = request.session.get("checkout_data")

        if not checkout_data:
            return redirect('cart')

        address = Address.objects.filter(
            user=request.user,
            is_default=True
        ).first()

        if not address:
            return redirect('address')

        # ✅ ORDER CREATE IS NOW IN ORDERS APP
        order = create_order_from_checkout(
            user=request.user,
            address=address,
            checkout_data=checkout_data
        )

        # ✅ PAYMENT ONLY RESPONSIBILITY
        Payment.objects.create(
            order=order,
            amount=order.total_amount,
            status="SUCCESS",
            method=request.POST.get("method", "COD")
        )

        # ✅ CLEAR SESSION
        request.session.pop("checkout_data", None)

        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()

        return redirect('order-success', order_id=order.id)