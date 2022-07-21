from decimal import Decimal
from typing import Tuple, List

from django.contrib.auth import get_user_model

from goods.models import Product
from shop.models import Cart, CartProduct, Order, Purchase

User = get_user_model()


class UserCart:

    def __init__(self, user: User) -> None:
        self.cart, *_ = Cart.objects.get_or_create(user=user)

    def add_to_cart(self, product: Product, quantity: int = 1) -> bool:
        if self.in_stock(product, quantity):
            cart_product = CartProduct.objects.filter(product=product).first()
            if not cart_product:
                CartProduct(product=product, cart=self.cart).save()
            else:
                cart_product.quantity += quantity
                cart_product.save(update_fields=['quantity'])
                self.cart.save()
            return True
        return False

    def products_in_cart(self) -> List:
        return self.cart.cart_products.select_related('product').all()

    @property
    def total_sum(self) -> Tuple[Decimal, int]:
        """Метод получения общей стоимости товаров в заказе"""
        total = Decimal(0.00)
        num_products = 0
        for item in self.products_in_cart():
            total += item.total_price
            num_products += item.quantity
        return Decimal(total), num_products

    def clear_cart(self):
        self.cart.delete()
        self.cart.save()

    def __len__(self):
        return len(self.cart.cart_products.all())

    @classmethod
    def in_stock(cls, product: Product, quantity: int) -> bool:
        if product.quantity > 0 and product.quantity >= quantity:
            return True
        return False

    @classmethod
    def write_off_qty(cls, order: Order) -> None:
        products = []
        for item in order.purchases.all():
            item.product.quantity -= item.qty
            products.append(item.product)
        Product.objects.bulk_update(products, ['quantity'])

    def add_to_purchase_history(self, order: Order) -> None:
        Purchase.objects.bulk_create([Purchase(product=item.product,
                                               user=self.cart.user,
                                               order=order,
                                               qty=item.quantity)
                                      for item in self.products_in_cart()])
