from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin

from . import serializers
from .models import SKU
from . import contants


class HotSKUListView(ListCacheResponseMixin, ListAPIView):
    """
    返回热销数据
    """
    serializer_class = serializers.SKUSerializer

    def get_queryset(self):
        return SKU.objects.filter(category_id=self.kwargs.get('category_id'), is_launched=True).order_by('-sales')[:contants.HOT_SKUS_COUNT_LIMIT]
