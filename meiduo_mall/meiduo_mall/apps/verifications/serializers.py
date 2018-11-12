# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/10 20:27'
from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging


logger = logging.getLogger('django')


class CheckImageCodeSerializer(serializers.Serializer):
    """
    图片验证码校验序列化器
    """
    image_code_id = serializers.UUIDField(help_text='图片验证码uuid编号')
    text = serializers.CharField(min_length=4, max_length=4, help_text='图片验证码内容')

    def validate(self, attrs):
        """
        对图片验证码进行校验
        :param attrs:
        :return:
        """
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 取redis连接对象
        redis_conn = get_redis_connection("verify_codes")
        # 获取真实的验证码
        real_image_code = redis_conn.get("img_%s" % image_code_id)
        if real_image_code is None:
            # 过期或者不存在
            raise serializers.ValidationError('无效的图片验证码')
        real_image_code = real_image_code.decode()

        # 删除redis中的图片验证码，防止用户对同一个验证码进行多次验证
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        # 通过类视图对象属性kwargs取出mobile
        mobile = self.context['view'].kwargs.get('mobile')
        if mobile:
            send_flag = redis_conn.get('send_flag_%s' % mobile)
            if send_flag:
                raise serializers.ValidationError('发送短信次数过于频繁')
        return attrs


