import uuid

from rest_framework.views import APIView
from rest_framework.response import Response

from api import models
from api.utils.base_response import BaseResponse


class AuthLogin(APIView):
    def post(self, request, *args, **kwargs):
        ret = BaseResponse()
        try:
            username = request.data.get("username")
            pwd = request.data.get("pwd")
            user = models.UserInfo.objects.filter(username=username, pwd=pwd).first()
            if not user:
                ret.code = 1001
                ret.error = "用户名或密码错误"
            else:
                token = str(uuid.uuid4())
                models.UserToken.objects.update_or_create(user=user, defaults={"token": token})
                ret.token = token
                ret.msg = "登录成功"
        except Exception as e:
            ret.code = 1003
            ret.error = '代码异常'
        return Response(ret.dict)