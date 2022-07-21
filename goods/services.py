import json
import logging
from csv import DictReader
from datetime import datetime
from typing import List, Dict, Union

from django.core import serializers
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from goods.models import Category, Product, ProductImportFile
from shop.models import Purchase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
fh = logging.FileHandler('import_log.txt', encoding='utf-8')
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_products(**kwargs) -> Union[QuerySet[Product], Product]:
    if kwargs.get('id'):
        return Product.objects.get(id=kwargs.get('id'))
    if kwargs.get('category_id'):
        category = get_object_or_404(Category, id=kwargs['category_id'])
        if category:
            return Product.objects.select_related('category').filter(category=category)
    elif kwargs.get('category_name'):
        category = get_object_or_404(Category, name=kwargs['category_name'])
        if category:
            return Product.objects.select_related('category').filter(category=category)
    return Product.objects.select_related('category').all()


class Import:
    def __init__(self, obj: ProductImportFile) -> None:
        self.obj = obj
        self.message_data = []

    def import_data(self, delimiter: str = ',', quotechar: str = '"') -> bool:
        """
        Метод импорта продуктов из файла
        """
        start_time = datetime.now()
        logger.info(f'{self.obj.file} starts import at {start_time}>')
        products_file = self.obj.file.read()
        try:
            products_str = products_file.decode().split('\n')
        except UnicodeDecodeError as err:
            logger.error(f'Error: Not a valid import', exc_info=err)
            return False
        csv_reader = DictReader(products_str, delimiter=delimiter, quotechar=quotechar)
        data = []
        for row in csv_reader:
            data.append(dict(row))
        all_products = [item['fields'] for item in json.loads(
            serializers.serialize('json', Product.objects.select_related('category').all())
        )]
        set_create = set.difference(
            set([item['article'] for item in data]),
            set([item['article'] for item in all_products])
        )

        create_data = [item for item in data if item['article'] in set_create]
        update_data = [item for item in data if item['article'] not in set_create]
        if create_data:
            self.create_products(create_data)
        if update_data:
            self.update_products(update_data)
        logger.info(f'{self.obj.file} finished importing which started in {start_time}>')
        self.save_log_info(start_time)
        return True

    def save_log_info(self, start_time: datetime) -> None:
        """
        Сохранение части лога в модель файла импорта
        """

        with open('import_log.txt', 'r') as imp_log:
            result = imp_log.read()
            file_log = result[result.find(f'Starts import at {start_time}>'):result.find(
                f'Finished importing which started in {start_time}')]
            self.obj.log_info = file_log
            self.obj.errors = file_log.count('Error:')
            self.obj.warnings = file_log.count('Warning:')
            self.obj.status = 'Complete'
            self.obj.save()

    def _get_cleaned_data(self, data: List[Dict]) -> List:
        cleaned_data = []
        for item in data:
            try:
                int(item['price'])
                int(item['quantity'])
                assert len(item['title']) > 0
                assert len(item['category']) > 0
                assert len(item['article']) > 0
                cleaned_data.append(item)
            except (ValueError, AssertionError, KeyError):
                self.message_data.append(item.get('article', 'unknown'))
        if self.message_data:
            logger.error(f'Error: The product with articles {self.message_data} '
                         f'will not created/updated: wrong data.')
        if cleaned_data:
            cleaned_data = self._get_or_create_categories(cleaned_data)
        self.message_data.clear()
        return cleaned_data

    def _get_or_create_categories(self, cleaned_data: List[Dict]) -> List[Dict]:
        for item in cleaned_data:
            category, created = Category.objects.get_or_create(name=item['category'])
            if created:
                self.message_data.append(category.name)
            item['category'] = category
        if self.message_data:
            logger.info(f'Info: New categories: {self.message_data} was created.')
            self.message_data.clear()
        return cleaned_data

    def create_products(self, create_data: List[Dict]) -> None:
        cleaned_data = self._get_cleaned_data(create_data)
        Product.objects.bulk_create([Product(**item) for item in cleaned_data], batch_size=100)

    def update_products(self, update_data: List[Dict]) -> None:
        logger.warning(
            f'Warning: The product with articles {tuple(item["article"] for item in update_data)} '
            f'already exists. There will be updating.')
        cleaned_data = self._get_cleaned_data(update_data)
        products = Product.objects.filter(article__in=[item['article'] for item in cleaned_data])
        cleaned_data = {item['article']: {'price': item['price'],
                                          'quantity': item['quantity'],
                                          'title': item['title'],
                                          'category': item['category']}
                        for item in cleaned_data}
        for item in products:
            item.price = cleaned_data[item.article]['price']
            item.quantity = cleaned_data[item.article]['quantity']
            item.title = cleaned_data[item.article]['title']
            item.category = cleaned_data[item.article]['category']
        Product.objects.bulk_update(products, ['price', 'quantity', 'title', 'category'], batch_size=100)


def get_report_purchases():
    purchases = Purchase.objects.select_related('product', 'order')\
                                .all()\
                                .values('purchase_date', 'product__title', 'qty', 'product__price')\
                                .order_by('-purchase_date')
    result = {}
    for item in list(purchases):
        key = str(item['purchase_date'])
        temp = {item['product__title']:
            {
                'price': item['product__price'], 'quantity': item['qty']
        }
        }
        if not result.get(key):
            result[key] = temp
        else:
            if item['product__title'] in result[key].keys():
                result[key][item['product__title']]['quantity'] += item['qty']
            else:
                result[key][item['product__title']] = temp[item['product__title']]
    total = 0
    for item in result.values():
        temp = [(x['quantity'], x['price']) for x in list(item.values())]
        item['summary quantity'] = sum([x[0] for x in temp])
        item['summary profit'] = sum([x[0]*x[1] for x in temp])
        total += item['summary profit']
    return result, total