# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/15 18:06'
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    url(r'cart/$', views.CartView.as_view())
]

