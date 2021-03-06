from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from alipay import AliPay
import os
from django.conf import settings

from orders.models import OrderInfo
from .models import Payment


class PaymentView(APIView):
    """
    支付宝支付
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        # 校验订单order_id
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单信息有误'}, status=status.HTTP_400_BAD_REQUEST)
        # 向支付宝发起请求
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        order_string = alipay_client.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )
        # 拼接链接
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return Response({'alipay_url': alipay_url})


class PaymentStatusView(APIView):
    """
    修改支付结果状态
    """
    def put(self, request):
        data = request.query_params.dict()
        sign = data.pop('sign')

        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        success = alipay_client.verify(data, sign)
        if success:
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')
            # 保存支付数据
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单数据
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
            return Response({'trade_id': trade_id})
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)
