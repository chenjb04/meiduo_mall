# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/13 19:51'

from rest_framework import serializers


from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    """
    行政区域序列化器
    """

    class Meta:
        model = Area
        fields = ['id', 'name']


class SubAreaSerializer(serializers.ModelSerializer):
    """
    子级行政区划信息序列化器
    """
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']

