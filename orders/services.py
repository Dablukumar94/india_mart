from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Order, OrderItem, OrderStatusHistory
from products.models import Product

from django.shortcuts import get_object_or_404
from carts.models import Cart


def get_checkout_items(user, session):
    """
    Returns: (items_list, is_buy_now)
    """

    buy_now_id = session.get('buy_now_product_id')

    if buy_now_id:
        product = get_object_or_404(Product, id=buy_now_id)
        quantity = session.get('buy_now_quantity', 1)

        return [{'product': product, 'quantity': quantity}], True

    cart = Cart.objects.filter(user=user).prefetch_related('items__product').first()

    if cart:
        items = [
            {'product': item.product, 'quantity': item.quantity}
            for item in cart.items.all()
        ]
        return items, False

    return [], False


def store_checkout_session(session, data):
    session["checkout_data"] = {
        "items": [
            {
                "product_id": str(item["product"].id),
                "quantity": item["quantity"]
            }
            for item in data["items"]
        ],
        "items_total": float(data["items_total"]),
        "delivery_fee": float(data["delivery_fee"]),
        "discount": float(data["discount"]),
        "total_amount": float(data["total_amount"]),
    }


def clear_buy_now_session(session):
    session.pop("buy_now_product_id", None)
    session.pop("buy_now_quantity", None)


# =========================
# ORDER CREATION
# =========================
@transaction.atomic
def create_order_from_checkout(user, address, checkout_data):

    order = Order.objects.create(
        user=user,
        address=address,
        items_total=checkout_data["items_total"],
        delivery_fee=checkout_data["delivery_fee"],
        discount=checkout_data["discount"],
        total_amount=checkout_data["total_amount"],
        status="PLACED",
    )

    items = []

    for item in checkout_data["items"]:

        product = get_safe_product(item["product_id"])

        if not product:
            continue  # skip deleted products safely

        items.append(
            OrderItem(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=item["quantity"],
            )
        )

    OrderItem.objects.bulk_create(items)

    return order


# =========================
# SAFE PRODUCT FETCH
# =========================
def get_safe_product(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None


# =========================
# STATUS TRANSITIONS
# =========================
ALLOWED_TRANSITIONS = {
    "PLACED": ["SHIPPED", "CANCELLED"],
    "SHIPPED": ["DELIVERED", "CANCELLED"],
    "DELIVERED": ["RETURN_REQUESTED", "REPLACEMENT_REQUESTED"],
    "RETURN_REQUESTED": ["PICKUP_SCHEDULED"],
    "PICKUP_SCHEDULED": ["PICKED_UP"],
}


# =========================
# STATUS UPDATE
# =========================
def update_order_status(order, new_status, user=None):

    old_status = order.status

    if old_status == new_status:
        return order

    allowed = ALLOWED_TRANSITIONS.get(old_status, [])

    if new_status not in allowed:
        raise ValueError(f"Invalid transition {old_status} → {new_status}")

    order.status = new_status

    timestamp_map = {
        "SHIPPED": "shipped_at",
        "DELIVERED": "delivered_at",
        "CANCELLED": "cancelled_at",
    }

    if new_status in timestamp_map:
        setattr(order, timestamp_map[new_status], timezone.now())

    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        old_status=old_status,
        new_status=new_status,
        changed_by=user
    )

    return order


# =========================
# CHECKOUT CALCULATION
# =========================

def calculate_checkout_data(items_list, coupon=None):

    # =========================
    # ITEMS TOTAL
    # =========================
    items_total = sum(
        item['product'].price * item['quantity']
        for item in items_list
    )
    items_total = Decimal(str(items_total))

    # =========================
    # DELIVERY RULE (DYNAMIC)
    # =========================
    FREE_DELIVERY_THRESHOLD = Decimal("1500.00")
    STANDARD_DELIVERY_FEE = Decimal("40.00")

    if items_total >= FREE_DELIVERY_THRESHOLD:
        delivery_fee = Decimal("0.00")
    else:
        delivery_fee = STANDARD_DELIVERY_FEE

    # =========================
    # DISCOUNT (DYNAMIC + FUTURE READY)
    # =========================
    discount = Decimal("0.00")

    if coupon:
        if coupon.get("type") == "flat":
            discount = Decimal(str(coupon.get("value", 0)))
        elif coupon.get("type") == "percent":
            discount = (items_total * Decimal(str(coupon.get("value", 0)))) / Decimal("100")

    # prevent negative discount
    if discount > items_total:
        discount = items_total

    # =========================
    # FINAL TOTAL
    # =========================
    total_amount = items_total + delivery_fee - discount

    return {
        "items_total": items_total,
        "delivery_fee": delivery_fee,
        "discount": discount,
        "total_amount": total_amount,
        "items": items_list
    }


# =========================
# AUTO CANCEL EXPIRED ORDERS
# =========================
def cancel_expired_pending_orders(expire_after_minutes=30):

    cutoff = timezone.now() - timedelta(minutes=expire_after_minutes)

    expired_orders = Order.objects.filter(
        status="PLACED",   # FIXED (safe fallback instead of PENDING_PAYMENT)
        placed_at__lt=cutoff,
    )

    cancelled_count = 0

    with transaction.atomic():
        for order in expired_orders.select_for_update():

            update_order_status(
                order=order,
                new_status="CANCELLED",
                user=None
            )

            cancelled_count += 1

    return cancelled_count