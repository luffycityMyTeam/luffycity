from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from api.models import *


class AuthToken(BaseAuthentication):

    def authenticate(self, request):
        token = request.GET.get("token")
        token_obj = UserToken.objects.filter(token=token).first()
        if not token_obj:
             raise exceptions.AuthenticationFailed({"code": 1001, "error": "认证失败"})
        return token_obj.user, token_obj  # 返回的两个值可以用 request.user 和 request.auth 取出来