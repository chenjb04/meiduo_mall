from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework.filters import OrderingFilter

from . import serializers
from .models import SKU
from . import contants


class HotSKUListView(ListCacheResponseMixin, ListAPIView):
    """
    返回热销数据
    """
    serializer_class = serializers.SKUSerializer
    pagination_class = None

    def get_queryset(self):
        return SKU.objects.filter(category_id=self.kwargs.get('category_id'), is_launched=True).order_by('-sales')[:contants.HOT_SKUS_COUNT_LIMIT]


class SKUListView(ListAPIView):
    """
    商品列表数据
    """
    queryset = SKU.objects.all()
    serializer_class = serializers.SKUSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)

