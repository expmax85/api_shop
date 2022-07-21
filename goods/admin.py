from django.contrib import admin

from goods.models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'article', 'price', 'quantity')
    change_list_template = 'admin/product_change_list.html'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
