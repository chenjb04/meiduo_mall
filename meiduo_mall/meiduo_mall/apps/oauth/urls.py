# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/12 21:11'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^qq/authorization/$', views.OAuthQQURLView.as_view()),

]