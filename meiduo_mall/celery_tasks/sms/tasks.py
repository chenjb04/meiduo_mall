# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/11 17:51'
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import celery_app


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信验证码异步任务
    :return:
    """
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, str(constants.SMS_CODE_REDIS_EXPIRES / 60)],
                          constants.SMS_CODE_TEMP_ID)