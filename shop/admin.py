from django.contrib import admin

from shop.models import Cart, Order, Purchase


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'fio', 'payment_method', 'phone', 'email')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_date', 'order', 'user', 'product', 'qty')
    change_list_template = 'admin/purchase_change_list.html'
    list_filter = ('purchase_date', 'user',
                   'order__id', 'product__title', 'product__category__name')
