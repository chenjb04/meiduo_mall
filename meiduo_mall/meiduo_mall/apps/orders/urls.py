# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/26 16:21'
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'orders/settlement/$', views.OrderSettlementView.as_view()),
    url(r'orders/$', views.SaveOrderView.as_view()),
    url(r'orders/(?P<pk>\d+)/uncommentgoods/$', views.UncommentGoodsView.as_view()),
    url(r'orders/\d+/comments/$', views.CommentsView.as_view()),
    url(r'skus/(?P<pk>\d+)/comments/$', views.SKUSCommentsView.as_view()),
]