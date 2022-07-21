from typing import Callable

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views import View
from django.conf import settings

from goods.services import get_products
from shop.forms import OrderForm
from shop.services import UserCart
from users.services import get_user


class PermMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('shop.add_cart', )


class AddToCart(PermMixin, View):
    """
    Adding product to cart. Only for verified users.
    """
    @classmethod
    def get(cls, request: HttpRequest, product_id: int) -> Callable:
        product = get_products(id=product_id)
        cart = UserCart(user=request.user)
        if not cart.add_to_cart(product):
            messages.add_message(request, settings.ERROR_QUANTITY, 'Not enough quantity in stock')
        return redirect(request.META.get('HTTP_REFERER'))


class CheckoutView(PermMixin, View):
    """
    Get checkout and make purchase. Only for verified users.
    """
    form_class = OrderForm
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> Callable:
        user = get_user(email=request.user.email)
        initial = {'fio': f'{user.first_name} {user.last_name}',
                   'email': user.email,
                   'phone': user.phone,
                   'city': user.city,
                   'address': user.address,
                   }
        form = self.form_class(initial=initial)
        return render(request, 'shop/checkout.html', {'form': form})

    def post(self, request: HttpRequest) -> Callable:
        form = self.form_class(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user_cart = UserCart(user=request.user)
                order = form.save()
                user_cart.add_to_purchase_history(order=order)
                user_cart.write_off_qty(order=order)
                user_cart.clear_cart()
            return render(request, 'shop/success_purchase.html')
        return render(request, 'shop/checkout.html', {'form': form})
