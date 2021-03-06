import random
from django_redis import get_redis_connection
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from meiduo_mall.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms_code
from . import constants
from . import serializers
from users.models import User


class ImageCodeView(APIView):
    """
    图片验证码
    """

    def get(self, request, image_code_id):
        # 生成验证码图片
        text, image = captcha.generate_captcha()
        # 获取redis连接对象
        redis_conn = get_redis_connection("verify_codes")
        # 设置图片验证码过期时间
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type="images/jpg")


class SMSCodeView(GenericAPIView):
    """
    短信验证码
    """
    serializer_class = serializers.CheckImageCodeSerializer

    def get(self, request, mobile):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        # print(sms_code)
        redis_conn = get_redis_connection('verify_codes')

        # 设置短信验证码过期时间
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 使用管道执行多个命令，减少连接数据库的开销
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 发送短信
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, str(constants.SMS_CODE_REDIS_EXPIRES / 60)],
        #                       constants.SMS_CODE_TEMP_ID)
        # 使用celery发布异步任务
        send_sms_code.delay(mobile, sms_code)

        return Response({'message': 'OK'})


class SMSCodeByTokenView(APIView):
    """
    根据access_token发送短信
    """
    def get(self, request):
        # 获取access_token
        access_token = request.query_params.get('access_token')
        if not access_token:
            return Response({'message': '缺少access_token'}, status=status.HTTP_400_BAD_REQUEST)
        # 验证access_token
        mobile = User.check_send_sms_code_token(access_token)
        if mobile is None:
            return Response({'message': '无效的access_token'}, status=status.HTTP_400_BAD_REQUEST)
        # 判断手机号发送的频率
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({'message': '发送短信次数过于频繁'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        # print(sms_code)
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()
        # 发送短信
        send_sms_code.delay(mobile, sms_code)
        return Response({'message': 'OK'})
