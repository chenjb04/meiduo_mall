from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings

from meiduo_mall.utils.models import BaseModel
from . import constants


class OAuthQQUser(BaseModel):
    """
    qq登录用户
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

    @staticmethod
    def generate_save_user_token(openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {'openid': openid}
        token = serializer.dumps(data)
        return token.decode()
