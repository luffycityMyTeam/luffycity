import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from django_redis import get_redis_connection  # 导入redis缓存
from api import models

from api.utils.auth_token import AuthToken  # 自己写的auth认证
from api.utils.base_response import BaseResponse  # 自己写的返回的类
from django.utils.decorators import method_decorator  # django自带的函数装饰器变为方法装饰器
from api.utils.wrappers.wrappers import ret_error  # 自己写的返回异常装饰器


class ShoppingCarView(ViewSetMixin, APIView):
    """购物车接口"""
    authentication_classes = [AuthToken]
    conn = get_redis_connection("default")  # redis连接

    # @method_decorator(ret_error)  # 报错返回异常信息装饰器
    def create(self, request, *args, **kwargs):  # post()
        ret = BaseResponse()
        # 1.获取用户提交课程ID和价格策略ID
        user_id = request.user.pk
        course_id = int(request.data.get('course_id'))
        price_policy_id = int(request.data.get('price_policy_id'))

        # 2.获取课程信息
        course_obj = models.Course.objects.filter(pk=course_id).first()
        if not course_obj:
            ret.error = '课程不存在'
            ret.code = 2001
            return Response(ret.dict)

        # 3.获取该课程的所有价格策略
        price_policy_list = course_obj.policy_list.all()
        price_policy_dict = {}
        for i in price_policy_list:
            price_policy_dict[i.id] = {
                'price': i.price,
                'policy': i.policy,
                'policy_display': i.get_policy_display()
            }
        print(price_policy_dict)

        # 4.判断用户提交策略是否合法
        if price_policy_id not in price_policy_dict:
            ret.code = 2001
            ret.error = '价格策略不合法'
            return Response(ret.dict)

        # 5.将购物车信息添加到redis当中
        shopping_car_key = 'shopping_car_%s_%s' % (user_id, course_id)
        shopping_car_dict = {
            'title': course_obj.title,
            'img': course_obj.course_img,
            'default_policy': price_policy_id,
            'policy': json.dumps(price_policy_dict),
        }
        print(shopping_car_dict)
        self.conn.hmset(shopping_car_key, shopping_car_dict)  # 放入redis缓存中
        ret.data = '添加成功'
        return Response(ret.dict)
