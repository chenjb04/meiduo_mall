# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/15 17:49'
from rest_framework import serializers

from .models import SKU


class SKUSerializer(serializers.ModelSerializer):
    """
    sku序列化器
    """
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']