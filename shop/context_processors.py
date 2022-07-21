from typing import Dict

from django.conf import settings
from django.http import HttpRequest

from shop.services import UserCart


def custom_context(request: HttpRequest) -> Dict:
    if request.user.is_authenticated:
        user_cart = UserCart(request.user)
        total = user_cart.total_sum
    else:
        user_cart = None
        total = (None, None)
    return {
        'VERIFY_TEST_MESSAGE': settings.VERIFY_TEST_MESSAGE,
        'ERROR_QUANTITY': settings.ERROR_QUANTITY,
        'SUCCESS_VERIFY': settings.SUCCESS_VERIFY,
        'cart': user_cart,
        'summary_price': total[0],
        'sum_quantity': total[1],
    }
