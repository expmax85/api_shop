from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

from goods.models import Product

User = get_user_model()


class Cart(models.Model):
    products = models.ManyToManyField(Product, through='CartProduct')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='carts')

    class Meta:
        verbose_name = 'cart'
        verbose_name_plural = 'carts'
        db_table = 'carts'

    def __str__(self) -> str:
        return f'Cart by {self.user}'


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    @property
    def total_price(self) -> Decimal:
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return f'{self.product} in cart'


class Order(models.Model):
    """
    Модель заказа
    """
    PAYMENT_CHOICES = [
        ('card', 'Bank Card'),
        ('cash', 'After delivery to courier'),
    ]
    fio = models.CharField(max_length=100, verbose_name='name and lastname')
    phone_valid = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=' '.join([str('phone number must be entered in the format:'), '+999999999',
                                                   str('up to 15 digits allowed.')]))
    phone = models.CharField(max_length=16, validators=[phone_valid], verbose_name='phone number')
    email = models.EmailField(verbose_name='email')
    city = models.CharField(max_length=25, verbose_name='city')
    address = models.TextField(max_length=255, verbose_name='address')
    payment_method = models.CharField(max_length=4,
                                      choices=PAYMENT_CHOICES,
                                      default='card',
                                      verbose_name='payment method')

    def __str__(self) -> str:
        return f'"Order №{self.id}'

    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'


class Purchase(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='purchases', verbose_name='#order ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='history_product')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='customer',
                             related_name='buyer')
    purchase_date = models.DateField(auto_now_add=True)
    qty = models.IntegerField()

    def __str__(self) -> str:
        return f'Purchase by {self.order} from {self.purchase_date:"%Y-%m-%d")}'

    class Meta:
        verbose_name = 'purchase'
        verbose_name_plural = 'purchases'
