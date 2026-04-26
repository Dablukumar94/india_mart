from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from products.models import Product

from .models import Cart, CartItem


def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class AddToCartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = get_user_cart(request.user)
        product = get_object_or_404(Product, id=pk)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save(update_fields=['quantity'])
        return redirect('product-list')


class CartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        cart = get_user_cart(request.user)
        items = list(cart.items.select_related('product'))
        total = sum(item.get_total_price() for item in items)

        return render(
            request,
            'products/cart.html',
            {
                'products': [item.product for item in items],
                'cart_items': items,
                'total': total,
            },
        )


class IncreaseQtyView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = get_user_cart(request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=pk)
        cart_item.quantity += 1
        cart_item.save(update_fields=['quantity'])
        return redirect('cart')


class DecreaseQtyView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = get_user_cart(request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=pk)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save(update_fields=['quantity'])
        else:
            cart_item.delete()
        return redirect('cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = get_user_cart(request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=pk)
        cart_item.delete()
        return redirect('cart')
