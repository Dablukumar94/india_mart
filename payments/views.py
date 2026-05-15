from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import Address
from .models import Payment
from carts.models import Cart


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

        address = Address.objects.filter(user=request.user, is_default=True).first()
        if not address:
            return redirect('address')

        # ✅ CREATE ORDER HERE (ONLY HERE)
        order = Order.objects.create(
            user=request.user,
            address=address,
            items_total=checkout_data["items_total"],
            delivery_fee=checkout_data["delivery_fee"],
            discount=checkout_data["discount"],
            total_amount=checkout_data["total_amount"],
            status="PLACED",
        )

        # ✅ CREATE ITEMS
        for item in checkout_data["items"]:
            product = Product.objects.get(id=item["product_id"])

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=item["quantity"],
            )

        # ✅ PAYMENT CREATE
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