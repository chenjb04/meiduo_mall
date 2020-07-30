from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from rest_framework.generics import GenericAPIView

from .utils import OAuthQQ
from .exceptions import QQAPIException
from .models import OAuthQQUser
from .serializers import OAuthQQUserSerializer


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


class OAuthQQUserView(GenericAPIView):
    """
    获取qq用户对应的美多商城用户
    """
    serializer_class = OAuthQQUserSerializer

    def get(self, request):
        # 提取code参数
        code = request.query_params.get('code')
        if not code:
            return Response({'message': "缺少code"}, status=status.HTTP_400_BAD_REQUEST)
        # 根据code向QQ服务器发起请求，获取access_token
        try:
            oauth_qq = OAuthQQ()
            access_token = oauth_qq.get_access_token(code)
            # 根据access_token向QQ服务器发起请求，获取openid
            openid = oauth_qq.get_openid(access_token)
        except QQAPIException:
            return Response({'message': '获取qq用户数据异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 根据openid查询用户是否在以前绑定过美多商城
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果未绑定 手动创建绑定access_token
            access_token = OAuthQQUser.generate_save_user_token(openid)
            return Response({'access_token': access_token})
        else:
            # 如果绑定 生成jwt token
            # 手动为用户生成jwt token
            user = oauth_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'token': token,
                'username': user.username,
                'user_id': user.id
            })

    def post(self, request):
        """
        对于首次QQ登录的用户，进行绑定用户
        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 手动为用户生成jwt token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({
            'token': token,
            'username': user.username,
            'user_id': user.id
        })


