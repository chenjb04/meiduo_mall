# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/26 16:09'
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from django_redis import get_redis_connection

from carts.serializers import CartSKUSerializer
from .models import OrderInfo, OrderGoods
from goods.models import SKU
from users.models import User


class OrderSettlementSerializer(serializers.Serializer):
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True, read_only=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    """
    保存订单序列化器
    """
    class Meta:
        model = OrderInfo
        fields = ['order_id', 'address', 'pay_method']
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """
        保存订单
        :param validated_data:
        :return:
        """
        # 获取当前下单用户
        user = self.context['request'].user
        # 创建订单编号
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ("%09d" % user.id)
        # 保存订单基本数据
        address = validated_data['address']
        pay_method = validated_data['pay_method']
        # 开启事务
        with transaction.atomic():
            # 创建保存点
            save_id = transaction.savepoint()
            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_amount=Decimal(0),
                    total_count=0,
                    freight=Decimal('10.0'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']
                    else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )

                # 从redis中获取购物车数据
                redis_conn = get_redis_connection('cart')
                cart_redis = redis_conn.hgetall("cart_%s" % user.id)
                cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

                cart = {}
                for sku_id in cart_selected:
                    cart[int(sku_id)] = int(cart_redis[sku_id])
                # sku_obj_list = SKU.objects.filter(id__in=cart.keys())
                # 遍历勾选要下单的商品数据
                sku_id_list = cart.keys()
                for sku_id in sku_id_list:
                    # 判断商品库存
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        origin_stock = sku.stock
                        origin_sales = sku.stock
                        if sku.stock < cart[sku.id]:
                            # 事务回滚
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError('商品库存不足')
                        # 减少商品库存
                        # sku.stock -= cart[sku.id]
                        # sku.sales += cart[sku.id]
                        # sku.save()
                        new_stock = origin_stock - cart[sku.id]
                        new_sales = origin_sales + cart[sku.id]
                        ret = SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if ret == 0:
                            continue

                        order.total_count += cart[sku.id]
                        order.total_amount += (sku.price * cart[sku.id])
                        # 保存
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=cart[sku.id],
                            price=sku.price
                        )
                        break
                order.save()
            except serializers.ValidationError:
                raise
            except Exception:
                transaction.savepoint_rollback(save_id)
                raise
            # 提交事务
            transaction.savepoint_commit(save_id)

            # 清除购物车已经结算的商品
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, *cart_selected)
            pl.srem('cart_selected_%s' % user.id, *cart_selected)
            pl.execute()
            return order


class DisplayOrderSerializer(serializers.ModelSerializer):
    # 展示订单列表的序列化器
    class Meta:
        model = SKU
        fields = '__all__'
        # fields=('name','price','default_image_url')
        # read_only_fields = ('name','price','default_image_url')


class DisplayOrderSerializers(serializers.ModelSerializer):
    # 嵌套
    sku = DisplayOrderSerializer()

    class Meta:
        model = OrderGoods
        fields = '__all__'


class DisplaysOrderSerializers(serializers.ModelSerializer):
    # 嵌套
    skus = DisplayOrderSerializers(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'


class UncommentSKUSerializers(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = '__all__'


class UncommentGoodsSerializers(serializers.ModelSerializer):
    sku = UncommentSKUSerializers()

    class Meta:
        model = OrderGoods
        fields = '__all__'


class CommentsSerializers(serializers.ModelSerializer):
    """验证获取的数据"""
    order = serializers.IntegerField()
    sku = serializers.IntegerField()
    comment = serializers.CharField()
    score = serializers.IntegerField()
    is_anonymous = serializers.BooleanField()

    class Meta:
        model = OrderGoods
        fields = ('order', 'sku', 'comment', 'is_anonymous', 'score', 'sku')

    def validate(self, attrs):
        order_id = int(attrs['order'])
        order = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        if not order:
            raise serializers.ValidationError('订单不存在')
        sku = SKU.objects.filter(id=attrs['sku'])
        if not sku:
            raise serializers.ValidationError('商品不存在')
        return attrs

    # 使用事物装饰器
    @transaction.atomic
    def create(self, validated_data):
        order_id = validated_data['order']
        sku_id = validated_data['sku']
        orders = OrderGoods.objects.get(order_id=order_id, sku_id=sku_id, is_commented=0)
        sku = SKU.objects.get(id=sku_id)
        sku.comments += 1
        sku.save()

        # 更新数据
        orders.comment = validated_data['comment']
        orders.score = validated_data['score']
        orders.is_anonymous = validated_data['is_anonymous']
        orders.is_commented = 1

        orders.save()
        count = OrderGoods.objects.filter(order_id=order_id, is_commented=0).count()
        if count == 0:
            try:
                orderinfo = OrderInfo.objects.get(order_id=order_id)
                orderinfo.status = 5
                orderinfo.save()
            except:
                raise serializers.ValidationError('订单状态修改失败')
        return validated_data


class SKUSCommentsUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)
        extra_kwargs = {
            'username': {
                'readonly': True
            }
        }


class SKUSCommentsSerializers(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        pass
    # username = SKUSCommentsUserSerializers()

    class Meta:
        model = OrderGoods
        fields = ('username', 'score', 'comment')
