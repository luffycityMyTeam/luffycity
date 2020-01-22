from rest_framework.response import Response



# 返回错误信息的装饰器
def ret_error(func):
    def inner(request, *args, **kwargs):
        try:
            f = func(request, *args, **kwargs)
        except Exception as e:
            ret = {"code": 1001, "error": "数据返回失败"}
            return Response(ret)
        return f
    return inner