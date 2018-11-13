from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings

from . import constants


class User(AbstractUser):
    """
    用户模型
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

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

    @staticmethod
    def check_send_sms_code_token(token):
        """
        检查access_token
        :return:
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, constants.SEND_SMS_COKE_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            mobile = data.get('mobile')
            return mobile

    def generate_set_password_token(self):
        """
        生成用户修改密码的token
        :return:
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, constants.SET_PASSWORD_TOKEN_EXPIRES)
        data = {
            'user_id': self.id
        }
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(token, user_id):
        """
        检查用户修改密码的access_token
        :return:
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, constants.SET_PASSWORD_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True

    def generate_email_verify_url(self):
        """
        生成邮箱验证链接
        :return:
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, constants.EMAIL_VERIFY_TOKEN_EXPIRES)
        data = {
            'user_id': self.id,
            'email': self.email
        }
        token = serializer.dumps(data)
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()
        return verify_url

    @staticmethod
    def check_email_verify_token(token):
        """
        校验邮链接token
        :return:
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, constants.EMAIL_VERIFY_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            User.objects.filter(id=user_id, email=email).update(email_active=True)
            return True




