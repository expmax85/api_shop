from django.db import models


class Category(models.Model):
    """
    Category model
    """
    name = models.CharField(
        max_length=25,
        null=True,
        verbose_name='category title',
        unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = 'categories'
        verbose_name = 'category'
        db_table = 'categories'


class Product(models.Model):
    """
    Product model
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='category',
    )
    title = models.CharField(max_length=100, verbose_name='product title')
    article = models.CharField(max_length=10, verbose_name='product article')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='price')
    quantity = models.IntegerField(verbose_name='quantity')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        db_table = 'products'


class ProductImportFile(models.Model):
    """
    Model for files by importing products
    """

    file = models.FileField(upload_to='import')
    errors = models.IntegerField(default=0)
    warnings = models.IntegerField(default=0)
    log_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(default='In progress', blank=True, max_length=24)

    def __str__(self) -> str:
        return f'Import {str(self.file)} from {str(self.created_at)}'

    class Meta:
        verbose_name = 'products_import'
        verbose_name_plural = 'products_imports'
        db_table = 'products_import'
