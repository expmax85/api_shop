from django.urls import path
from goods import views


app_name = 'goods'
urlpatterns = [
    path('', views.IndexView.as_view(), name='main_page'),

    path('products/import/', views.ImportView.as_view(), name='import'),
    path('products/reports/', views.ReportView.as_view(), name='reports')
    ]
