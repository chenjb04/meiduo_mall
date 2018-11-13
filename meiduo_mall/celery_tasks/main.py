# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/11 17:41'
from celery import Celery
import os


if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


celery_app = Celery('meiduo')
celery_app.config_from_object('celery_tasks.config')
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
# 开启celery方法
# celery -A 应用路径 （.包路径） worker -l info -P eventlet
# celery -A celery_tasks.main worker -l info -P eventlet
