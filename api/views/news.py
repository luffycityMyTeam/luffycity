from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers.news import *
from django.utils.decorators import method_decorator  # 把函数装饰器变为方法装饰器
from api.utils.wrappers.wrappers import ret_error  # 导入装饰器
from rest_framework.viewsets import ViewSetMixin
from api.utils.auth_token import AuthToken

class ArticleView(ViewSetMixin, APIView):
    authentication_classes = [AuthToken]

    @method_decorator(ret_error)  # 报错返回异常信息装饰器
    def list(self, request, *args, **kwargs):
        ret = {"code": 1000}
        queryset_liu = Article.objects.filter(position=0)
        ser_liu = ArticleSerializers(queryset_liu, many=True)
        ret["article_liu"] = ser_liu.data

        queryset_big = Article.objects.filter(position=1)
        ser_big = ArticlePositionSerializers(queryset_big, many=True)
        ret["article_big"] = ser_big.data

        queryset_small = Article.objects.filter(position=2)
        ser_small = ArticlePositionSerializers(queryset_small, many=True)
        ret["article_small"] = ser_small.data

        return Response(ret)

    @method_decorator(ret_error)  # 报错返回异常信息装饰器
    def retrieve(self, request, *args, **kwargs):
        ret = {"code": 1000}
        pk = kwargs.get("pk")
        article_obj = Article.objects.filter(pk=pk).first()
        ser = ArticleSerializers(article_obj)
        ret["articl"] = ser.data

        article_obj.view_num = article_obj.view_num +1
        article_obj.save()

        comment_obj_list = article_obj.comment
        ser_comment = CommentSerializers(comment_obj_list, many=True)
        ret["comment"] = ser_comment.data

        return Response(ret)

    def update(self, request, *args, **kwargs):  # put请求 http://127.0.0.1:9527/api/v1/news/
        ret = {"code": 1000}
        article_id = kwargs.get("pk")
        article_obj = Article.objects.filter(pk=article_id).first()

        content = request.data.get("content")
        user = request.user
        p_id = request.data.get("p_id")
        print(p_id)
        if not p_id:
            Comment.objects.create(content_object=article_obj, content=content, user=user)
        else:
            Comment.objects.create(content_object=article_obj, content=content, user=user, p_node_id=p_id)
        ret["data"] = content
        return Response(ret)

