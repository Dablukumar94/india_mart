from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Address
from carts.models import Cart, CartItem
from payments.models import Payment
from products.models import Product

from .models import Order


class OrderSuccessUrlFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='secret123')
        self.address = Address.objects.create(
            user=self.user,
            full_name='Test User',
            mobile='9999999999',
            address='123 Test Street',
            district='Test District',
            state='Test State',
            pincode='123456',
            is_default=True,
        )
        self.product = Product.objects.create(
            name='Phone',
            description='Sample product',
            price='499.00',
        )

    def test_checkout_redirects_to_payment_detail_with_order_id(self):
        self.client.login(username='tester', password='secret123')
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        response = self.client.post(reverse('checkout'))

        order = Order.objects.get(user=self.user)
        self.assertRedirects(
            response,
            reverse('payment-detail', kwargs={'order_id': order.id}),
        )

    def test_process_payment_redirects_to_order_success_with_order_id(self):
        order = Order.objects.create(
            user=self.user,
            address=self.address,
            total_amount='499.00',
            status='PLACED',
        )
        payment = Payment.objects.create(
            order=order,
            method='COD',
            status='PENDING',
            amount='499.00',
        )

        response = self.client.post(
            reverse('process-payment', kwargs={'pk': payment.id}),
            {'method': 'UPI'},
        )

        self.assertRedirects(
            response,
            reverse('order-success', kwargs={'order_id': order.id}),
        )
