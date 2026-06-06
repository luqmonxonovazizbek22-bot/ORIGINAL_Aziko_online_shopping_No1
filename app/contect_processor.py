from .models import Cart

def cart_data(request):
    if not request.user.is_authenticated:
        return {
            'cart_items_count': 0,
            'cart_total_amount': 0
        }

    cart = Cart.objects.filter(
        user=request.user,
        checked_out=False
    ).first()

    if not cart:
        return {
            'cart_items_count': 0,
            'cart_total_amount': 0
        }

    return {
        'cart_items_count': cart.total_quantity,
        'cart_total_amount': cart.total_price,
    }