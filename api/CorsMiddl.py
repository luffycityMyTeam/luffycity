from django.utils.deprecation import MiddlewareMixin

class CorsMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        # 添加响应头

        # 允许你的域名来获取我的数据
        response["Access-Control-Allow-Origin"] = "*"

        # 允许携带Content-Type请求头
        response["Access-Control-Allow-Headers"] = "Content-Type"

        # 允许你发送DELETE,PUT请求
        response["Access-Control-Allow-Methods"] = "DELETE,PUT"
        return response
