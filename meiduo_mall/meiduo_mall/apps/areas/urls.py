# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/13 19:51'

from django.conf.urls import url
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('areas', views.AreasViewSet, base_name='area')
urlpatterns =[

]
urlpatterns += router.urls