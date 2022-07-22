from typing import Callable

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from goods.forms import ImportForm
from goods.models import Product
from goods.services import Import, get_products, \
    get_report_purchases


class IndexView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'goods/index.html'

    def get_queryset(self) -> QuerySet:
        return get_products()


class SuperUserRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> Callable:
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ImportView(SuperUserRequiredMixin, View):
    form_class = ImportForm
    template_name = 'admin/import_products.html'

    def get(self, request: HttpRequest) -> Callable:
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request: HttpRequest) -> Callable:
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            imp = Import(file)
            imp.import_data()
            messages.add_message(request, messages.SUCCESS, 'The products was successfully added. Se the import_log for details import.')
            return redirect('admin:index')
        return redirect(request.META.get('HTTP_REFERER'))


class ReportView(SuperUserRequiredMixin, View):
    template_name = 'admin/reports.html'

    def get(self, request: HttpRequest, **kwargs) -> Callable:
        result, total = get_report_purchases()
        return render(request, self.template_name, context={'result': result,
                                                            'total': total})
