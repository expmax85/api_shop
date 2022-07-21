from django.db.models import QuerySet
from rest_framework import filters
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from goods.exceptions import WrongQueryParams
from goods.serializers import ProductSerializer
from goods.services import get_products


ALLOW_PARAMS = ['category_id', 'category', 'search', 'offset', 'limit']


class ProductViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self) -> QuerySet:
        wrong_params = [x for x in self.request.query_params.keys()
                        if x not in ALLOW_PARAMS]
        category_name = self.request.query_params.get('category')
        category_id = self.request.query_params.get('category_id')
        if wrong_params or all([category_name, category_id]):
            raise WrongQueryParams

        queryset = get_products(category_id=category_id, category_name=category_name)
        return queryset
