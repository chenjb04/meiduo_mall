from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from . import serializers


class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """
    list
    返回所有省市的信息

    retrieve
    返回特定省市的下属行政规划
    """
    # queryset = Area.objects.all()
    # 关闭分页处理
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer
