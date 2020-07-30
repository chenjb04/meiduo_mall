# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/15 20:57'

from rest_framework.pagination import PageNumberPagination


class StandardPageNumPagination(PageNumberPagination):
    """
    分页
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20
