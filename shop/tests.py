from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from goods.models import Product, Category
from shop.models import Order
from shop.services import UserCart

User = get_user_model()


class ShopTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='test@user.com', password='testp@sw0rd',
                                            first_name='user',
                                            last_name='test', phone='79222222222')
        category = Category.objects.create(name='test_category')
        cls.product = Product.objects.create(title='test', article='123we', price=123,
                                             quantity=1, category=category)
        cls.perm = Permission.objects.get(codename='add_cart')

    def test_cart(self):
        """
        Теестирование корзины
        """
        cart = UserCart(user=self.user)
        self.assertEqual(len(cart), 0)

        # добавление в корзину товара
        cart.add_to_cart(self.product)
        self.assertEqual(len(cart), 1)

        # добавление дополнительной единицы товара не увеличивает размера корзины
        cart.add_to_cart(self.product)
        self.assertEqual(len(cart), 1)

        # добавлени в корзину другого товара
        category = Category.objects.get(id=1)
        product = Product.objects.create(title='test2', article='12343', price=100,
                                         quantity=2, category=category)
        cart.add_to_cart(product)
        self.assertEqual(len(cart), 2)

        # тестирование суммарной информации по корзине
        total, qty = cart.total_sum
        self.assertEqual(total, 346)
        self.assertEqual(qty, 3)

        # тестирование проверки наличия товара на складе
        self.assertTrue(cart.in_stock(product, 1))
        self.assertFalse(cart.in_stock(product, 3))

        # тестирование совершения покупки
        order = Order.objects.create(fio=self.user.first_name, phone=self.user.phone, email=self.user.email,
                                     city='testcity', address='testaddress')
        cart.add_to_purchase_history(order=order)
        cart.write_off_qty(order=order)
        self.assertEqual(product.quantity, 2)

        # очистка корзины
        cart.clear_cart()
        self.assertEqual(len(cart), 0)

    def test_view_cart(self):
        """
        Добавление в корзину верифицированным и неверифицированным пользователем
        """
        self.client.login(email=self.user.email, password='testp@sw0rd')
        response = self.client.get(reverse('shop-polls:add_to_cart', kwargs={'product_id': self.product.id}),
                                   HTTP_REFERER='http://127.0.0.1/', follow=False)
        self.assertEqual(response.status_code, 403)
        self.user.user_permissions.add(self.perm)
        response = self.client.get(reverse('shop-polls:add_to_cart', kwargs={'product_id': self.product.id}),
                                   HTTP_REFERER='http://127.0.0.1/', follow=False)
        self.assertEqual(response.status_code, 302)

