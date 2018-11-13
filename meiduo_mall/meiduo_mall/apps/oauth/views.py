from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import OAuthQQ


class OAuthQQURLView(APIView):
    """
    提供qq登录的网址
    """
    def get(self, request):
        # 提取state参数
        state = request.query_params.get('state')
        if not state:
            state = '/'
        # 拼接QQ用户登录链接
        oauth_qq = OAuthQQ(state=state)
        login_url = oauth_qq.generate_qq_login_url()
        return Response({
            'oauth_url': login_url,
        })
