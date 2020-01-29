from rest_framework.response import Response


# 返回错误信息的装饰器
def ret_error(func):
    def inner(request, *args, **kwargs):
        try:
            f = func(request, *args, **kwargs)
        except Exception as e:
            ret = {"code": 1002, "error": "代码异常,数据返回失败"}
            return Response(ret)
        return f

    return inner
