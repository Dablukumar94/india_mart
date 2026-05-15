from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.http import HttpResponse

from reportlab.pdfgen import canvas

from accounts.models import Address
from carts.models import Cart, CartItem
from products.models import Product
from payments.models import Payment
from reviews.models import Review

from .models import Order, OrderItem, OrderStatusHistory



def update_order_status(order, new_status, user=None):
    old_status = order.status

    if old_status == new_status:
        return

    order.status = new_status
    order.save(update_fields=["status"])

    OrderStatusHistory.objects.create(
        order=order,
        old_status=old_status,
        new_status=new_status,
        changed_by=user
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

        items = list(order.items.all())  # ✅ ek baar fetch

        # -------- TRACKING FLOW --------
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

        # -------- PAYMENT --------
        payment = Payment.objects.filter(order=order).first()

        # -------- REVIEWS --------
        product_ids = [item.product_id for item in items]

        reviews = Review.objects.filter(
            user=request.user,
            product_id__in=product_ids
        )

        review_map = {r.product_id: r.rating for r in reviews}

        # attach review data to items
        for item in items:
            item.already_reviewed = item.product_id in review_map
            item.user_rating = review_map.get(item.product_id, 0)

        # -------- FINAL RESPONSE --------
        return render(request, "orders/order_detail.html", {
            "order": order,
            "items": items,   # ✅ important (use this in template)
            "steps": steps,
            "current_index": current_index,
            "payment": payment
        })

# =========================
# CHECKOUT
# =========================
def calculate_checkout_data(items_list):
    """
    items_list should be a list of objects/dicts containing 'product' and 'quantity'
    """
    items_total = sum(item['product'].price * item['quantity'] for item in items_list)
    
    delivery_fee = Decimal("50.00")
    discount = Decimal("10.00")
    total_amount = items_total + delivery_fee - discount

    return {
        "items_total": items_total,
        "delivery_fee": delivery_fee,
        "discount": discount,
        "total_amount": total_amount,
        "items": items_list # List of {'product': p, 'quantity': q}
    }


# =========================
# SHOW CHECKOUT PAGE
# =========================

class CheckoutView(LoginRequiredMixin, View):
    login_url = 'login'

    def get_checkout_items(self, request):
        # 1. Check if "Buy Now" is active
        buy_now_id = request.session.get('buy_now_product_id')
        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            quantity = request.session.get('buy_now_quantity', 1)
            return [{'product': product, 'quantity': quantity}], True

        # 2. Otherwise, get from Cart
        cart = Cart.objects.filter(user=request.user).prefetch_related('items__product').first()
        if cart:
            items = [{'product': item.product, 'quantity': item.quantity} for item in cart.items.all()]
            return items, False
        
        return [], False

    def get(self, request):
        address = Address.objects.filter(user=request.user, is_default=True).first()
        items_list, is_buy_now = self.get_checkout_items(request)

        if not items_list:
            return redirect('cart') # Cart empty hai aur Buy Now bhi nahi hai

        data = calculate_checkout_data(items_list)
        
        context = {
            "address": address,
            "cart_items": data["items"],
            "items_total": data["items_total"],
            "delivery_fee": data["delivery_fee"],
            "discount": data["discount"],
            "total_amount": data["total_amount"],
            "is_buy_now": is_buy_now
        }
        return render(request, "orders/checkout.html", context)

    def post(self, request):

        address = Address.objects.filter(user=request.user, is_default=True).first()
        if not address:
            return redirect('address')

        items_list, is_buy_now = self.get_checkout_items(request)
        if not items_list:
            return redirect('cart')

        data = calculate_checkout_data(items_list)

        # 🔥 SAVE DATA ONLY (NO DB)
        request.session["checkout_data"] = {
            "items": [
                {
                    "product_id": str(item["product"].id),
                    "quantity": item["quantity"]
                }
                for item in data["items"]
            ],
            "items_total": str(data["items_total"]),
            "delivery_fee": str(data["delivery_fee"]),
            "discount": str(data["discount"]),
            "total_amount": str(data["total_amount"]),
        }

        return redirect('payment-detail')   # no order_id
    

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
        # Purana Buy Now data saaf karein aur naya set karein
        request.session['buy_now_product_id'] = str(pk)
        request.session['buy_now_quantity'] = 1
        return redirect('checkout')

# =========================
# CANCEL
# =========================
class CancelOrderView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in ['PLACED', 'SHIPPED']:

            old_status = order.status
            order.status = 'CANCELLED'
            order.save(update_fields=['status'])

            update_order_status(
                order=order,
                old_status=old_status,
                new_status="CANCELLED",
                user=request.user
            )

        return redirect('order-history')


# =========================
# RETURN / REPLACE
# =========================    
class ReturnOrderView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        action = request.POST.get("action")

        if order.status != "DELIVERED":
            return redirect('order-history')

        if action == "return":
            new_status = "RETURN_REQUESTED"

        elif action == "replace":
            new_status = "REPLACEMENT_REQUESTED"

        else:
            return redirect('order-history')
        
        old_status = order.status
        order.status = new_status
        order.save(update_fields=["status"])

        update_order_status(
            order=order,
            old_status=old_status,
            new_status=new_status,
            user=request.user
        )

        return redirect('order-history')



# =========================
# INVOICE (FIXED)
# =========================
class InvoiceView(LoginRequiredMixin, View):

    def get(self, request, order_id):

        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            id=order_id,
            user=request.user
        )

        payment = Payment.objects.filter(order=order).first()

        # ❌ NO CALCULATION HERE
        items_total = order.items_total
        delivery_fee = order.delivery_fee
        discount = order.discount
        total_amount = order.total_amount

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

        p.drawString(50, y, f"Items Total: ₹{items_total:.2f}")
        y -= 15
        p.drawString(50, y, f"Delivery: ₹{delivery_fee:.2f}")
        y -= 15
        p.drawString(50, y, f"Discount: ₹{discount:.2f}")
        y -= 20
        p.drawString(50, y, f"TOTAL: ₹{total_amount:.2f}")

        p.showPage()
        p.save()

        return response