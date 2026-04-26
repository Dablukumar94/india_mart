def cart_count(request):
    total_items = 0
    if request.user.is_authenticated and hasattr(request.user, 'cart'):
        total_items = sum(item.quantity for item in request.user.cart.items.all())

    return {'cart_count': total_items}
