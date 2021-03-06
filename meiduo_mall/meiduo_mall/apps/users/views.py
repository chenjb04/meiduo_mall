from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView
from django_redis import get_redis_connection
import re
from rest_framework_jwt.views import ObtainJSONWebToken

from . import serializers
from orders.serializers import DisplaysOrderSerializers
from .models import User
from verifications.serializers import CheckImageCodeSerializer
from .utils import get_user_by_account
from . import constants
from goods.models import SKU
from goods.serializers import SKUSerializer
from carts.utils import merge_cart_cookie_to_redis
from orders.models import OrderInfo, OrderGoods


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


class EmailView(UpdateAPIView):
    """
    保存邮箱
    """
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    """
    验证邮箱链接
    """
    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 对token进行校验
        result = User.check_email_verify_token(token)
        if result:
            return Response({'message': 'OK'})
        else:
            return Response({'message': '非法token'}, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户收货地址新增与修改
    """
    serializer_class = serializers.AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.get_queryset()
        serializer = serializers.AddressSerializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 检查用户保存地址数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已经达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        address = self.get_object()

        # 逻辑删除
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserHistoryView(mixins.CreateModelMixin, GenericAPIView):
    """
    用户浏览记录
    """
    serializer_class = serializers.AddUserHistorySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        保存
        :param request:
        :return:
        """
        return self.create(request)

    def get(self, request):
        user_id = request.user.id
        redis_conn = get_redis_connection('history')
        sku_id_list = redis_conn.lrange('history_%s' % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)

        sku_list = list()
        for sku_id in sku_id_list:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        serializer = SKUSerializer(sku_list, many=True)
        return Response(serializer.data)


class UserAuthorizationView(ObtainJSONWebToken):
    """
    用户登录认证实现
    """
    def post(self, request, *args, **kwargs):
        """
        重写jwt post方法，对登录用户数据进行验证
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user') or request.user
            response = merge_cart_cookie_to_redis(request, response, user)
        return response


class OrderListView(ListAPIView):
    """
    个人中心订单列表显示
    """

    serializer_class = DisplaysOrderSerializers
    # queryset = OrderGoods.objects.all()

    def get_queryset(self):
        pass

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = OrderInfo.objects.filter(user_id=user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)













