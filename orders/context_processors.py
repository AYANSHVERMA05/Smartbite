from .models import Cart


def cart_context(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                return {
                    'cart_items_count': cart.total_items(),
                    'cart_total_price': cart.total_price(),
                }
        except Exception:
            pass
    return {
        'cart_items_count': 0,
        'cart_total_price': 0,
    }

