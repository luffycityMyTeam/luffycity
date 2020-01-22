from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer  # 渲染器组件
from rest_framework.versioning import QueryParameterVersioning, URLPathVersioning  # 获取版本组件
from rest_framework.viewsets import ViewSetMixin
from api.serializers.course import *
from api.utils.auth_token import AuthToken

class CourseView(ViewSetMixin, APIView):
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]  # 返回的数据渲染页面时显示的 数据样式

    def list(self, request, *args, **kwargs):
        print(request.version)  # 获取版本

        ret = {"code": 1000, "data": None}
        try:
            queryset = Course.objects.all()
            ser = CourseSerializers(instance=queryset, many=True)
            ret['data'] = ser.data
        except Exception as e:
            print(e)
            ret['code'] = 1001
            ret['error'] = '获取课程失败'
        return Response(ret)

    def retrieve(self, request, *args, **kwargs):
        ret = {"code": 1000, "data": None}
        # try:
        pk = kwargs.get("pk")
        obj = CourseDetail.objects.filter(course__pk=pk).first()
        print(obj)
        ser = CourseDetailSerializers(obj)
        ret['data'] = ser.data
        return Response(ret)


class MicroView(APIView):
    authentication_classes = [AuthToken]
    def get(self, request, *args, **kwargs):
        print(request.user)
        print(request.auth)
        return Response("微课程")
