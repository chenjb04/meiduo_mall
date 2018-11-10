from django.shortcuts import render
from django_redis import get_redis_connection
from django.http import HttpResponse
from rest_framework.views import APIView

from meiduo_mall.libs.captcha.captcha import captcha
from . import constants


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

