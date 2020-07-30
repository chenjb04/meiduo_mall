# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/15 17:49'
from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer

from .models import SKU
from .search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):
    """
    sku序列化器
    """
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']


class SKUIndexSerializer(HaystackSerializer):
    """
    haystack序列化器
    """
    class Meta:
        index_classes = [SKUIndex]
        fields = ['text', 'id', 'name', 'price', 'default_image_url', 'comments']
