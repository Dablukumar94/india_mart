from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from decimal import Decimal

from accounts.models import Address

from payments.models import Payment
from reviews.models import Review
from orders.models import Order

from orders.services import (
    get_checkout_items,
    calculate_checkout_data,
    store_checkout_session,
    clear_buy_now_session,
    update_order_status
)



# =========================
# ORDER DETAIL
# =========================
class OrderDetailView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):

        order = get_object_or_404(
            Order.objects.prefetch_related("items__product"),
            id=pk,
            user=request.user
        )

        items = list(order.items.all())

        normal_steps = [
            ("PLACED", "Order Placed", "✔"),
            ("SHIPPED", "Shipped", "✔"),
            ("DELIVERED", "Delivered", "✔"),
        ]

        return_steps = [
            ("RETURN_REQUESTED", "Return Requested", "✔"),
            ("PICKUP_SCHEDULED", "Pickup Scheduled", "✔"),
            ("PICKED_UP", "Completed", "✔"),
        ]

        cancel_steps = [
            ("PLACED", "Order Placed", "✔"),
            ("CANCELLED", "Cancelled", "✔"),
        ]

        if order.status == "CANCELLED":
            steps = cancel_steps
        elif order.status in ["RETURN_REQUESTED", "PICKUP_SCHEDULED", "PICKED_UP"]:
            steps = normal_steps + return_steps
        else:
            steps = normal_steps

        status_order = [s[0] for s in steps]
        current_index = status_order.index(order.status) if order.status in status_order else 0

        payment = Payment.objects.filter(order=order).first()

        product_ids = [item.product_id for item in items]

        reviews = Review.objects.filter(
            user=request.user,
            product_id__in=product_ids
        )

        review_map = {r.product_id: r.rating for r in reviews}

        for item in items:
            item.already_reviewed = item.product_id in review_map
            item.user_rating = review_map.get(item.product_id, 0)

        return render(request, "orders/order_detail.html", {
            "order": order,
            "items": items,
            "steps": steps,
            "current_index": current_index,
            "payment": payment
        })


# =========================
# CHECKOUT
# =========================
class CheckoutView(LoginRequiredMixin, View):
    login_url = 'login'

    def get_default_address(self, user):
        return Address.objects.filter(
            user=user,
            is_default=True
        ).first()

    def get(self, request):
        address = self.get_default_address(request.user)

        if not address:
            return redirect('address')

        items_list, is_buy_now = get_checkout_items(request.user, request.session)

        if not items_list:
            return redirect('cart')

        data = calculate_checkout_data(items_list)

        return render(request, "orders/checkout.html", {
            "address": address,
            "cart_items": data["items"],
            "items_total": data["items_total"],
            "delivery_fee": data["delivery_fee"],
            "discount": data["discount"],
            "total_amount": data["total_amount"],
            "is_buy_now": is_buy_now
        })

    def post(self, request):
        address = self.get_default_address(request.user)

        if not address:
            return redirect('address')

        items_list, _ = get_checkout_items(request.user, request.session)

        if not items_list:
            return redirect('cart')

        data = calculate_checkout_data(items_list)

        store_checkout_session(request.session, data)
        clear_buy_now_session(request.session)

        return redirect('payment-detail')


# =========================
# SUCCESS
# =========================
class OrderSuccessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/success.html', {'order': order})


# =========================
# HISTORY
# =========================
class OrderHistoryView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'orders/order_history.html', {'orders': orders})


# =========================
# BUY NOW
# =========================
class BuyNowView(LoginRequiredMixin, View):
    def get(self, request, pk):
        request.session['buy_now_product_id'] = str(pk)  # FIX: UUID safe
        request.session['buy_now_quantity'] = 1
        return redirect('checkout')


# =========================
# CANCEL ORDER
# =========================
class CancelOrderView(LoginRequiredMixin, View):

    def post(self, request, order_id):

        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in ['PLACED', 'SHIPPED']:

            update_order_status(
                order=order,
                new_status="CANCELLED",
                user=request.user
            )

        return redirect('order-history')


# =========================
# RETURN / REPLACE
# =========================
class ReturnOrderView(LoginRequiredMixin, View):

    def post(self, request, order_id):

        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "DELIVERED":
            return redirect('order-history')

        action = request.POST.get("action")

        status_map = {
            "return": "RETURN_REQUESTED",
            "replace": "REPLACEMENT_REQUESTED"
        }

        new_status = status_map.get(action)

        if not new_status:
            return redirect('order-history')

        update_order_status(
            order=order,
            new_status=new_status,
            user=request.user
        )

        return redirect('order-history')


# =========================
# INVOICE (PRODUCTION SAFE)
# =========================
class InvoiceView(LoginRequiredMixin, View):

    def get(self, request, order_id):

        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            id=order_id,
            user=request.user
        )

        payment = Payment.objects.filter(order=order).first()

        items_total = order.items_total or Decimal("0")
        delivery_fee = order.delivery_fee or Decimal("0")
        discount = order.discount or Decimal("0")
        total_amount = order.total_amount or Decimal("0")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'

        p = canvas.Canvas(response)

        p.setFont("Helvetica-Bold", 16)
        p.drawString(220, 800, "INVOICE")

        p.setFont("Helvetica", 10)
        p.drawString(50, 770, f"Order ID: {order.id}")
        p.drawString(50, 755, f"Customer: {order.user.username}")
        p.drawString(50, 740, f"Date: {order.created_at.strftime('%d-%m-%Y')}")
        p.drawString(50, 725, f"Paid By: {payment.method if payment else 'COD'}")

        y = 690
        for item in order.items.all():
            line = f"{item.product_name} x {item.quantity} = ₹{item.price}"
            p.drawString(50, y, line)
            y -= 18

        y -= 20
        p.setFont("Helvetica-Bold", 10)

        p.drawString(50, y, f"Items Total: ₹{items_total}")
        y -= 15
        p.drawString(50, y, f"Delivery: ₹{delivery_fee}")
        y -= 15
        p.drawString(50, y, f"Discount: ₹{discount}")
        y -= 20
        p.drawString(50, y, f"TOTAL: ₹{total_amount}")

        p.showPage()
        p.save()

        return response