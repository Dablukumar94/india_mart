# from django.shortcuts import render, redirect
# from django.contrib import messages

# # Create your views here.

# # messages.success(request, "Data saved successfully!")
# # messages.error(request, "Something went wrong!")
# # messages.warning(request, "Please check your form!")
# # messages.info(request, "Welcome back!")

# def index_page(request):
#     messages.success(request, "Data saved successfully!")
#     return render(request, "base/base.html")


from django.views import View
from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin

class ProductListView(View):

    def get(self, request):
        product_list = Product.objects.all()

        paginator = Paginator(product_list, 8)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        return render(request, "products/plp.html", {"products": products})
    

class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        return render(request, "products/pdp.html", {"product": product})
    

class AddToCartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = request.session.get('cart', {})

        product_id = str(pk)

        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1

        request.session['cart'] = cart

        return redirect('product-list')
    

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


# ➕ Increase quantity
class IncreaseQtyView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        cart = request.session.get('cart', {})

        product_id = str(pk)

        if product_id in cart:
            cart[product_id] += 1

        request.session['cart'] = cart
        return redirect('cart')


# ➖ Decrease quantity
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


# ❌ Remove item
class RemoveFromCartView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        cart = request.session.get('cart', {})

        product_id = str(pk)

        if product_id in cart:
            del cart[product_id]

        request.session['cart'] = cart
        return redirect('cart')


class CheckoutView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        return render(request, 'products/checkout.html')

    def post(self, request):
        cart = request.session.get('cart', {})

        if not cart:
            return redirect('cart')

        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        district = request.POST.get('district')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        total = 0

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            mobile=mobile,
            address=address,
            district=district,
            state=state,
            pincode=pincode,
            total_amount=0,
            status='PLACED'
        )

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)

            subtotal = product.price * quantity
            total += subtotal

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        order.total_amount = total
        order.save()

        # clear cart
        request.session['cart'] = {}

        return redirect('order-success')


class OrderSuccessView(View):
    def get(self, request):
        return render(request, 'products/success.html')
    


class OrderHistoryView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        return render(request, 'products/order_history.html', {
            'orders': orders
        })


class OrderDetailView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        order = Order.objects.get(id=pk, user=request.user)

        return render(request, 'products/order_detail.html', {
            'order': order
        })