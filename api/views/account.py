
from rest_framework.views import APIView
from rest_framework.response import Response
from api import models
import uuid


class AuthLogin(APIView):
    def post(self, request, *args, **kwargs):
        ret = {}
        username = request.data.get("username")
        pwd = request.data.get("pwd")
        print(username, pwd)
        user = models.UserInfo.objects.filter(username=username, pwd=pwd).first()
        if not user:
            ret["code"] = 1001
            ret["error"] = "用户名或密码错误"
        else:
            token = str(uuid.uuid4())
            models.UserToken.objects.update_or_create(user=user, defaults={"token": token})
            ret["code"] = 1000
            ret["token"] = token
            ret["msg"] = "登录成功"
        return Response(ret)