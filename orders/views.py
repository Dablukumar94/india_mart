from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import Address
from carts.models import Cart, CartItem
from products.models import Product

from .models import Order, OrderItem


class CheckoutView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        address = Address.objects.filter(user=request.user, is_default=True).first()
        cart = Cart.objects.filter(user=request.user).prefetch_related('items__product').first()
        items = list(cart.items.all()) if cart else []
        total = sum(item.get_total_price() for item in items)

        return render(
            request,
            'orders/checkout.html',
            {
                'address': address,
                'cart_items': items,
                'total': total,
            },
        )

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).prefetch_related('items__product').first()
        if not cart or not cart.items.exists():
            return redirect('cart')

        address = Address.objects.filter(user=request.user, is_default=True).first()
        if not address:
            return redirect('address')

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=0,
            status='PLACED',
        )

        total = 0
        for item in cart.items.select_related('product'):
            product = item.product
            subtotal = product.price * item.quantity
            total += subtotal
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )

        order.total_amount = total
        order.save(update_fields=['total_amount'])
        cart.items.all().delete()
        return redirect('payment-detail', order_id=order.id)


class OrderSuccessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        return render(request, 'orders/success.html', {
            'order': order
        })


class OrderHistoryView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'orders/order_history.html', {'orders': orders})


class OrderDetailView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        return render(request, 'orders/order_detail.html', {'order': order})


class BuyNowView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        product = get_object_or_404(Product, id=pk)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        return redirect('checkout')

class CancelOrderView(View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        # ❗ Only allow cancel if not delivered
        if order.status in ['PLACED', 'SHIPPED']:
            order.status = 'CANCELLED'
            order.save()

        return redirect('order-history')
