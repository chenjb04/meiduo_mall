# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/11/20 19:49'
import base64
import pickle
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    合并购物车，cookie保存到redis中
    :param request:
    :param response:
    :param user:
    :return:
    """
    # 从cookie中取出购物车数据
    cart_str = request.COOKIES.get('cart')
    if not cart_str:
        return response
    cookie_cart = pickle.loads(base64.b64decode(cart_str.encode()))

    # 从redis中取出购物车数据
    redis_conn = get_redis_connection('cart')
    cart_redis = redis_conn.hgetall('cart_%s' % user.id)
    redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

    cart = {}
    for sku_id, count in cart_redis.items():
        cart[int(sku_id)] = int(count)

    for sku_id, selected_count_dict in cookie_cart.items():
        cart[sku_id] = selected_count_dict['count']
        if selected_count_dict['selected']:
            redis_cart_selected.add(sku_id)

    # 将cookie中的购物车合并到redis
    pl = redis_conn.pipeline()
    pl.hmset('cart_%s' % user.id, cart)
    pl.sadd('cart_selected_%s' % user.id, *redis_cart_selected)
    pl.execute()

    # 删除cookie中的购物车数据
    response.delete_cookie('cart')
    return response
