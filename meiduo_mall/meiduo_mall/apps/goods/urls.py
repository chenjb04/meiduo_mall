# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/15 18:06'
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns =[
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
    url(r'^categories/(?P<pk>\d+)/$', views.GoodCategoryView.as_view()),
]
router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')
urlpatterns += router.urls
