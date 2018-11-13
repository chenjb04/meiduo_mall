# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/12 20:53'
from django.conf import settings
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
import logging
import json

from .exceptions import QQAPIException

logger = logging.getLogger('django')


class OAuthQQ(object):
    """
    用户QQ登录的工具类
    """
    def __init__(self, app_id=None, app_key=None, redirect_url=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_url = redirect_url or settings.QQ_REDIRECT_URL
        self.state = state or settings.QQ_STATE

    def generate_qq_login_url(self):
        """
        拼接QQ用户登录链接地址
        :return:
        """
        url = 'https://graph.qq.com/oauth2.0/authorize?'
        data = {
            'response_type': 'code',
            'client_id': self.app_id,
            'redirect_uri': self.redirect_url,
            'state': self.state,
            'scope': 'get_user_info'
        }
        query_string = urlencode(data)
        url += query_string
        return url

    def get_access_token(self, code):
        """
        根据code向QQ服务器发起请求，获取access_token
        :return:
        """
        url = 'https://graph.qq.com/oauth2.0/token?'
        req_data = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'code': code,
            'redirect_uri': self.redirect_url,
        }
        url += urlencode(req_data)
        try:
            response = urlopen(url)
            response = response.read().decode()
            response_dict = parse_qs(response)
            access_token = response_dict.get('access_token')[0]
        except Exception as e:
            logger.error(e)
            raise QQAPIException('获取access_token异常')
        return access_token

    def get_openid(self, access_token):
        """
         根据access_token向QQ服务器发起请求，获取openid
        :return: 
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        try:
            response = urlopen(url)
            response = response.read().decode()
            data = json.loads(response[10:-4])
        except Exception as e:
            data = parse_qs(response)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException('获取openid异常')
        openid = data.get('openid', None)
        return openid

