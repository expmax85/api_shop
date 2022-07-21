import random

from django.core.management.base import BaseCommand

from goods.models import Category, Product


class Command(BaseCommand):
    """ Реализует импорт товаров у продавца из json """

    def handle(self, *args, **options) -> None:
        categories = Category.objects.all()
        if not categories:
            Category.objects.bulk_create(Category(name=f'test_category_{i}') for i in range(1, 4))
        n = 1
        products = Product.objects.all()
        if not products:
            articles = random.sample(range(100000, 999999), 15)
            categories = Category.objects.all()
            Product.objects.bulk_create(Product(title=f'test_product_{i}',
                                                article=str(articles[i]),
                                                category=random.choice(list(categories)),
                                                quantity=random.randint(1, 20),
                                                price=random.randrange(50, 500, 25)) for i in range(1, 15))