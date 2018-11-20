# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/20 17:28'
from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """
    购物车序列化器
    """
    sku_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(default=True)

    def validate(self, attrs):
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        count = attrs['count']
        if sku.stock < count:
            raise serializers.ValidationError('商品数量不足')

        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')


class CartDeleteSerializer(serializers.Serializer):
    """
    购物车序列化器
    """
    sku_id = serializers.IntegerField(min_value=1)

    def validate_sku_id(self, value):
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value
