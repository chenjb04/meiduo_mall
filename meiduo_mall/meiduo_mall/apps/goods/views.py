from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers
from .models import SKU, GoodsCategory
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


class GoodCategoryView(APIView):
    """
    商品分类
    """
    def get(self, request, pk):
        # 获取三级分类对象
        cat3 = GoodsCategory.objects.get(id=pk)
        # 获取二级分类对象和一级分类对象
        cat2 = cat3.parent
        cat1 = cat2.parent

        return Response({
            'cat1': cat1.name,
            'cat2': cat2.name,
            'cat3': cat3.name,

        })
