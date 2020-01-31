

from django.urls import path, include, re_path
from api.views import news, account, shopping_car, course

urlpatterns = [
    # 账户
    path('authLogin/', account.AuthLogin.as_view()),

    # 课程
    path('course/', course.CourseView.as_view({"get": "list"})),
    re_path(r'^course/(?P<pk>(\d+))', course.CourseView.as_view({"get": "retrieve"})),

    # 微课程
    path('micro/', course.MicroView.as_view()),

    # 深科技
    path('news/', news.ArticleView.as_view({"get": "list"})),
    re_path(r'^news/(?P<pk>(\d+))', news.ArticleView.as_view({"get": "retrieve",
                                                              'put': 'update',
                                                              # 'patch': 'partial_update',
                                                              # 'delete': 'destroy'
                                                              })),
    # path('ajax/', ajax.get_up),

    # 购物车
    path('shopping_car/', shopping_car.ShoppingCarView.as_view()),
    # 购物车结算
    path('payment/', shopping_car.PaymentView.as_view()),

]
