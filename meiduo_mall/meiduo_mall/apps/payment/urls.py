# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/12/1 14:47'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
    url(r'^payment/status/$', views.PaymentStatusView.as_view()),
]