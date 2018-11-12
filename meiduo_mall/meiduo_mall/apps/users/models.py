from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings

from . import constants


class User(AbstractUser):
    """
    用户模型
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def generate_send_sms_code_token(self):
        """
        生成发送短信验证码的access_token
        :return:access_token
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, constants.SEND_SMS_COKE_TOKEN_EXPIRES)
        data = {
            'mobile': self.mobile,
        }
        token = serializer.dumps(data)
        return token.decode()
