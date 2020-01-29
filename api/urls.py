

from django.urls import path, include, re_path
from api.views.course import CourseView, MicroView
from api.views.news import *
from api.views.account import *
from api.views.shopping_car import *
urlpatterns = [
    path('authLogin/', AuthLogin.as_view()),

    path('course/', CourseView.as_view({"get": "list"})),
    re_path(r'^course/(?P<pk>(\d+))', CourseView.as_view({"get": "retrieve"})),

    path('micro/', MicroView.as_view()),


    path('news/', ArticleView.as_view({"get": "list"})),
    re_path(r'^news/(?P<pk>(\d+))', ArticleView.as_view({"get": "retrieve",
                                                              'put': 'update',
                                                              # 'patch': 'partial_update',
                                                              # 'delete': 'destroy'
                                                              })),
    # path('ajax/', ajax.get_up),

    path('shopping_car/', ShoppingCarView.as_view({"post": "create"})),

]
