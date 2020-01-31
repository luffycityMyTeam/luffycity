import datetime
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
from django.conf import settings  # 导入配置文件


class ShoppingCarView(APIView):
    """购物车接口"""
    authentication_classes = [AuthToken]
    conn = get_redis_connection("default")  # redis连接

    @method_decorator(ret_error)  # 报错返回异常信息装饰器
    def post(self, request, *args, **kwargs):  # post(http://127.0.0.1:9527/api/v1/shopping_car/)
        """添加课程到购物车"""
        ret = BaseResponse()
        # 1.获取用户提交课程ID和价格策略ID
        user_id = request.user.pk
        course_id = int(request.data.get('course_id'))
        policy_id = int(request.data.get('policy_id'))

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
        if policy_id not in price_policy_dict:
            ret.code = 2001
            ret.error = '价格策略不合法'
            return Response(ret.dict)

        # 5.将购物车信息添加到redis当中
        shopping_car_key = settings.SHOPPING_CAR_KEY % (user_id, course_id)
        shopping_car_dict = {
            'title': course_obj.title,
            'img': course_obj.course_img,
            'default_policy': policy_id,
            'policy': json.dumps(price_policy_dict),
        }
        print(shopping_car_dict)
        self.conn.hmset(shopping_car_key, shopping_car_dict)  # 放入redis缓存中
        ret.data = '添加成功'
        return Response(ret.dict)

    @method_decorator(ret_error)  # delete(http://127.0.0.1:9527/api/v1/shopping_car)
    def delete(self, request, *args, **kwargs):
        """删除购买课程"""
        ret = BaseResponse()
        user_id = request.user.pk
        course_id_list = request.data.get("course_id")

        # 列表推导式 获取所有key
        key_list = [settings.SHOPPING_CAR_KEY % (user_id, course_id) for course_id in course_id_list]
        self.conn.delete(*key_list)  # 从redis中删除多条数据

        ret.data = '删除成功'
        return Response(ret.dict)

    @method_decorator(ret_error)  # patch(http://127.0.0.1:9527/api/v1/shopping_car)
    def patch(self, request, *args, **kwargs):
        """修改价格策略"""
        ret = BaseResponse()
        # 1.获取课程id, 价格策略id
        user_id = request.user.pk
        course_id = int(request.data.get("course_id"))
        policy_id = str(request.data.get("policy_id"))

        # 2.拼接key，并判断是否有课程id
        key = settings.SHOPPING_CAR_KEY % (user_id, course_id)
        if not self.conn.exists(key):
            ret.error = "课程不存在"
            ret.code = "1001"
            return Response(ret.dict)

        # 3.redis中获取所有价格策略
        policy_list = json.loads(self.conn.hget(key, "policy").decode())  # 注意loads回来int类型会变成str类型
        print(policy_list)
        if policy_id not in policy_list:
            ret.error = "价格策略不存在"
            ret.code = 1001
            return Response(ret.dict)

        # 4.修改redis中的默认价格策略
        self.conn.hset(key, "default_policy", policy_id)
        ret.data = '价格策略修改成功'
        return Response(ret.dict)

    @method_decorator(ret_error)  # get(http://127.0.0.1:9527/api/v1/shopping_car)
    def get(self, request, *args, **kwargs):
        """获取购物车中所有商品"""
        ret = BaseResponse()
        # 1.获取用户id
        user_id = request.user.pk

        # 2.拼接key
        key_match = settings.SHOPPING_CAR_KEY % (user_id, "*")

        # 3.返回
        course_list = []
        for key in self.conn.scan_iter(key_match, count=10):
            title = self.conn.hget(key, 'title').decode("utf-8")
            course_id = models.Course.objects.get(title=title).pk
            info = {
                "course_id": course_id,
                "title": title,
                "img": self.conn.hget(key, 'img').decode("utf-8"),
                "policy": json.loads(self.conn.hget(key, 'policy').decode("utf-8")),
                "default_policy": self.conn.hget(key, 'default_policy').decode("utf-8")
            }
            course_list.append(info)
        ret.data = course_list

        return Response(ret.dict)


class PaymentView(APIView):
    """结算接口"""
    authentication_classes = [AuthToken]
    conn = get_redis_connection("default")

    @method_decorator(ret_error)  # http://127.0.0.1:9527/api/v1/payment/
    def post(self, request, *args, **kwargs):  # post(http://127.0.0.1:9527/api/v1/payment/)
        ret = BaseResponse()
        # 获取课程 id列表
        course_list = request.data.get("course_list")

        # 0.清空用户redis(结算)的信息
        for key in self.conn.scan_iter(settings.PAYMENT_KEY % (request.user.pk, "*")):
            self.conn.delete(key)
        self.conn.delete(settings.PAYMENT_GLOBAL_KEY % request.user.pk)

        # 1.获redis(购物车中)获取课程的详细信息
        payment_dict_all = {}
        for course_id in course_list:
            key = settings.SHOPPING_CAR_KEY % (request.user.pk, course_id)
            if not self.conn.exists(key):
                ret.error = "购物车中没有该数据(%s)" % key
                ret.code = 1001
                return Response(ret.dict)

            default_policy_id = self.conn.hget(key, 'default_policy').decode("utf-8")
            policy_list = json.loads(self.conn.hget(key, 'policy').decode("utf-8"))
            policy = policy_list[default_policy_id]
            payment_dict = {
                "course_id": course_id,
                "title": self.conn.hget(key, "title").decode("utf-8"),
                "course_img": self.conn.hget(key, "img").decode("utf-8"),
                "coupon": {},
                "default_coupon": 0
            }
            payment_dict.update(policy)  # 字典的 update方法 可以把policy 的值跟新到payment_dict中
            payment_dict_all[course_id] = payment_dict
            # self.conn.hmset(payment_key, payment_dict)

        # 2.获取所有优惠券
        payment_global_dict = {'coupon': {}}
        ctime = datetime.date.today()  # 获取当前时间(年-月-日)
        # 过滤出用户可以使用的优惠券 lte小于等于, gte大于等于
        user_coupons = models.CouponRecord.objects.filter(user=request.user,
                                                          status=0,
                                                          coupon__valid_begin_date__lte=ctime,
                                                          coupon__valid_end_date__gte=ctime)
        for coupon in user_coupons:
            if not coupon.coupon.object_id:
                info = {}
                info["content_type"] = coupon.coupon.coupon_type
                info["content_type_display"] = coupon.coupon.get_coupon_type_display()
                if coupon.coupon.coupon_type == 0:  # 立减券
                    info["money_equivalent_value"] = coupon.coupon.money_equivalent_value
                elif coupon.coupon.coupon_type == 1:  # 满减券
                    info["money_equivalent_value"] = coupon.coupon.money_equivalent_value
                    info["minimum_consume"] = coupon.coupon.minimum_consume
                else:  # 打折券
                    info["off_percent"] = coupon.coupon.off_percent
                    info["minimum_consume"] = coupon.coupon.minimum_consume
                # 把通用优惠券添加到新的字典中
                payment_global_dict['coupon'][coupon.pk] = info
                payment_global_dict["default_coupon"] = 0
                continue

            info = {}
            course_nid = coupon.coupon.object_id
            info["content_type"] = coupon.coupon.coupon_type
            info["content_type_display"] = coupon.coupon.get_coupon_type_display()
            if coupon.coupon.coupon_type == 0:  # 立减券
                info["money_equivalent_value"] = coupon.coupon.money_equivalent_value
            elif coupon.coupon.coupon_type == 1:  # 满减券
                info["money_equivalent_value"] = coupon.coupon.money_equivalent_value
                info["minimum_consume"] = coupon.coupon.minimum_consume
            else:  # 打折券
                info["off_percent"] = coupon.coupon.off_percent
                info["minimum_consume"] = coupon.coupon.minimum_consume
            # 把优惠券和课程绑定
            if course_nid in payment_dict_all:
                # print(info)
                # print(json.dumps(info))
                payment_dict_all[course_nid]["coupon"][coupon.pk] = info
        # 3.存入redis中
        for k, v in payment_dict_all.items():  # k = course_id
            payment_key = settings.PAYMENT_KEY % (request.user.pk, k)
            v["coupon"] = json.dumps(v["coupon"])
            self.conn.hmset(payment_key, v)
        payment_global_key = settings.PAYMENT_GLOBAL_KEY % request.user.pk
        payment_global_dict["coupon"] = json.dumps(payment_global_dict["coupon"])
        self.conn.hmset(payment_global_key, payment_global_dict)

        print(payment_dict_all)
        print(payment_global_dict)
        ret.data = '添加结算成功'
        return Response(ret.dict)

    @method_decorator(ret_error)  # http://127.0.0.1:9527/api/v1/payment/
    def patch(self, request, *args, **kwargs):
        ret = BaseResponse()
        course_id = request.data.get("course_id")
        course_id = str(course_id) if course_id else course_id
        coupon_id = str(request.data.get("coupon_id"))

        payment_global_key = settings.PAYMENT_GLOBAL_KEY % request.user.pk
        payment_key = settings.PAYMENT_KEY % (request.user.pk, course_id)

        # 全站优惠券修改
        if not course_id:
            if coupon_id == "0":
                # 不使用全站优惠券
                self.conn.hset(payment_global_key, "default_coupon", "0")
                ret.data = '修改成功'
                return Response(ret.dict)
            global_coupon = json.loads(self.conn.hget(payment_global_key, "coupon").decode())
            if coupon_id not in global_coupon:
                ret.code = 1001
                ret.error = '优惠券不存在'
                return Response(ret.dict)
            self.conn.hset(payment_global_key, "default_coupon", coupon_id)
            ret.data = '修改成功'
            return Response(ret.dict)
        # 课程优惠券修改
        if coupon_id == "0":
            # 不使用课程优惠券
            self.conn.hset(payment_key, "default_coupon", "0")
            ret.data = '修改成功'
            return Response(ret.dict)
        course_coupon = json.loads(self.conn.hget(payment_key, 'coupon').decode())
        if coupon_id not in course_coupon:
            ret.code = 1001
            ret.error = '优惠券不存在'
            return Response(ret.dict)
        self.conn.hset(payment_key, "default_coupon", coupon_id)
        ret.data = '修改成功'
        return Response(ret.dict)

    @method_decorator(ret_error)  # http://127.0.0.1:9527/api/v1/payment/
    def get(self,request, *args, **kwargs):
        ret = BaseResponse()
        coupon_key = settings.PAYMENT_KEY % (request.user.pk, "*")
        coupon_global_key = settings.PAYMENT_GLOBAL_KEY % request.user.pk

        coupon_list = []
        for item in self.conn.scan_iter(coupon_key):
            print(item)
            course_dict = self.conn.hgetall(item)
            info = {}
            for k, v in course_dict.items():
                if k.decode() == "coupon":
                    info[k.decode()] = json.loads(v.decode())
                else:
                    info[k.decode()] = v.decode()
            coupon_list.append(info)
        print(coupon_list)
        coupon_global_dict = {}
        coupon_global_dict["coupon"] = json.loads(self.conn.hget(coupon_global_key, "coupon").decode())
        coupon_global_dict["default_coupon"] = self.conn.hget(coupon_global_key, "default_coupon").decode()
        ret.data = {
            "coupon_list": coupon_list,
            "coupon_global_dict": coupon_global_dict
        }
        return Response(ret.dict)
