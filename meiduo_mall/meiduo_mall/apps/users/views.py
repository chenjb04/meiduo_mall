from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
import re

from . import serializers
from .models import User
from verifications.serializers import CheckImageCodeSerializer
from .utils import get_user_by_account


class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserView(CreateAPIView):
    """
    用户注册
    """
    serializer_class = serializers.CreateUserSerializer


class SMSCodeTokenView(GenericAPIView):
    serializer_class = CheckImageCodeSerializer
    """
    获取发送短信验证码的凭据
    """
    def get(self, request, account):
        # 校检图片验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = get_user_by_account(account)
        if user is None:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        access_token = user.generate_send_sms_code_token()
        # 修改手机号
        mobile = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', user.mobile)
        return Response({
            'mobile': mobile,
            'access_token': access_token,
        })


class PasswordTokenView(GenericAPIView):
    """
    获取修改密码的token
    """
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        # 校检短信验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = get_user_by_account(account)
        if user is None:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 生成用于修改密码的access_token
        access_token = user.generate_set_password_token()
        return Response({
            'user_id': user.id,
            'access_token': access_token
        })


class PasswordView(mixins.UpdateModelMixin, GenericAPIView):
    """
    重置密码
    """
    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, pk):
        return self.update(request, pk)


class UserDetailView(RetrieveAPIView):
    """
    用户个人中心详细信息
    """
    serializer_class = serializers.UserDetailSerializer
    # 通过认证才能访问接口的权限
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        返回请求的用户对象
        :return:
        """
        return self.request.user






