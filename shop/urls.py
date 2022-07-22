from django.urls import path
from shop import views


app_name = 'shop'
urlpatterns = [
    path('add_to_cart/<int:product_id>', views.AddToCart.as_view(), name='add_to_cart'),
    path('clear_cart/', views.ClearCartView.as_view(), name='clear_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    ]
