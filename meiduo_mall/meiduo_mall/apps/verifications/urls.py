# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/10 19:25'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'image_codes/(?P<image_code_id>\d+/$)', views.ImageCodeView.as_view()),
]