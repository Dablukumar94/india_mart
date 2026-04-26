from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from .models import Product, Order, OrderItem, Address


# --------------------
# PRODUCT LIST
# --------------------
class ProductListView(View):
    def get(self, request):
        product_list = Product.objects.all()

        paginator = Paginator(product_list, 8)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        return render(request, "products/plp.html", {"products": products})


# --------------------
# PRODUCT DETAIL
# --------------------
class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        return render(request, "products/pdp.html", {"product": product})


# --------------------
# ADD TO CART
# --------------------
class AddToCartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = request.session.get('cart', {})

        product_id = str(pk)

        cart[product_id] = cart.get(product_id, 0) + 1

        request.session['cart'] = cart

        return redirect('product-list')


# --------------------
# CART VIEW
# --------------------
class CartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        cart = request.session.get('cart', {})
        products = []
        total = 0

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            product.quantity = quantity
            product.subtotal = product.price * quantity

            total += product.subtotal
            products.append(product)

        return render(request, 'products/cart.html', {
            'products': products,
            'total': total
        })


# --------------------
# CHECKOUT VIEW (FIXED)
# --------------------

class CheckoutView(LoginRequiredMixin, View):
    login_url = 'login'

    # 🟢 SHOW CHECKOUT PAGE
    def get(self, request):

        # ⭐ ADDRESS FETCH (HERE IS YOUR LINE)
        address = Address.objects.filter(
            user=request.user,
            is_default=True
        ).first()

        # 🛒 CART DATA
        cart = request.session.get('cart', {})
        products = []
        total = 0

        for product_id, qty in cart.items():
            product = Product.objects.get(id=product_id)
            product.quantity = qty
            product.subtotal = product.price * qty
            total += product.subtotal
            products.append(product)

        return render(request, 'products/checkout.html', {
            'address': address,   # 👈 send to template
            'products': products,
            'total': total
        })

    # 🔵 PLACE ORDER
    def post(self, request):

        cart = request.session.get('cart', {})

        if not cart:
            return redirect('cart')

        # ⭐ SAME ADDRESS LOGIC HERE ALSO
        address = Address.objects.filter(
            user=request.user,
            is_default=True
        ).first()

        if not address:
            return redirect('address')

        # 🧾 CREATE ORDER
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=0,
            status='PLACED'
        )

        total = 0

        for product_id, qty in cart.items():
            product = Product.objects.get(id=product_id)

            subtotal = product.price * qty
            total += subtotal

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price
            )

        order.total_amount = total
        order.save()

        # 🧹 CLEAR CART
        request.session['cart'] = {}

        return redirect('order-success')

# --------------------
# BUY NOW
# --------------------
class BuyNowView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        request.session['cart'] = {str(pk): 1}
        return redirect('checkout')


# --------------------
# ADDRESS VIEW (FIXED)
# --------------------
class AddressView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        address = Address.objects.filter(
            user=request.user,
            is_default=True
        ).first()

        return render(request, "products/edit_address.html", {
            "address": address
        })

    def post(self, request):

        Address.objects.filter(user=request.user).update(is_default=False)

        Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            mobile=request.POST.get('mobile'),
            address=request.POST.get('address'),
            district=request.POST.get('district'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            is_default=True
        )

        return redirect('checkout')


# --------------------
# ORDER SUCCESS
# --------------------
class OrderSuccessView(View):
    def get(self, request):
        return render(request, 'products/success.html')


# --------------------
# ORDER HISTORY
# --------------------
class OrderHistoryView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        return render(request, 'products/order_history.html', {
            'orders': orders
        })


# --------------------
# ORDER DETAIL
# --------------------
class OrderDetailView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)

        return render(request, 'products/order_detail.html', {
            'order': order
        })

class IncreaseQtyView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = request.session.get('cart', {})

        product_id = str(pk)

        if product_id in cart:
            cart[product_id] += 1

        request.session['cart'] = cart
        return redirect('cart')


class DecreaseQtyView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = request.session.get('cart', {})

        product_id = str(pk)

        if product_id in cart:
            cart[product_id] -= 1
            if cart[product_id] <= 0:
                del cart[product_id]

        request.session['cart'] = cart
        return redirect('cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = request.session.get('cart', {})

        product_id = str(pk)

        if product_id in cart:
            del cart[product_id]

        request.session['cart'] = cart
        return redirect('cart')