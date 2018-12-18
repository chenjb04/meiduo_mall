from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView

from goods.models import SKU
from .serializers import OrderSettlementSerializer, SaveOrderSerializer
from .models import OrderGoods
from .serializers import UncommentGoodsSerializers, CommentsSerializers


class OrderSettlementView(APIView):
    """
    订单结算
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        获取
        """
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.selected = True

        # 运费
        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """
    保存订单
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SaveOrderSerializer


class UncommentGoodsView(APIView):
    '''
    未评论商品
    页面加载，前段发送请求
    获取前端发送的order_id
    校验order_id
    通过订单id查询出订单中的商品信息（查询数据库，获取商品名称，商品价格，分数，是否匿名）反序列化
    返回相应

    '''

    def get(self, request, pk):
        goods = OrderGoods.objects.filter(order_id=pk, is_commented=False)
        ser = UncommentGoodsSerializers(goods, many=True)
        return Response(ser.data)


class CommentsView(APIView):
    """
    评论商品
    修改订单状态
    """

    def post(self, request):
        '''
        从json中获取数据
        序列化器验证数据
        保存数据
        返回响应
        :param data:
        :return:
        '''
        ser = CommentsSerializers(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'message': 'ok'})


class SKUSCommentsView(ListAPIView):

    # def get(self, request, pk):
    #     comments = OrderGoods.objects.filter(sku=pk, is_commented=True)
    #     ser = SKUSCommentsSerializers(comments, many=True)
    #     return Response(ser.data)
    def get_queryset(self):
        obj = OrderGoods.objects.filter(sku=self.kwargs['pk'], is_commented=1)
        return obj

    def get(self, request, *args, **kwargs):
        orders = self.get_queryset()
        comments = []
        for order in orders:
            comment = {}
            comment['comment'] = order.comment
            comment['username'] = order.order.user.username
            comment['score'] = order.score
            if order.is_anonymous:
                comment['is_anonymous'] = comment['username'][0]+'***'+comment['username'][-1]
            comments.append(comment)
        return Response(comments)