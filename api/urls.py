

from django.urls import path, include, re_path
from api.views.course import CourseView, MicroView
from api.views import account
from api.views import news
from api.views import ajax
urlpatterns = [
    path('course/', CourseView.as_view({"get": "list"})),

    re_path(r'^course/(?P<pk>(\d+))', CourseView.as_view({"get": "retrieve"})),

    path('micro/', MicroView.as_view()),

    path('authLogin/', account.AuthLogin.as_view()),

    path('news/', news.ArticleView.as_view({"get": "list"})),
    re_path(r'^news/(?P<pk>(\d+))', news.ArticleView.as_view({"get": "retrieve",
                                                              'put': 'update',
                                                              # 'patch': 'partial_update',
                                                              # 'delete': 'destroy'
                                                              })),
    # path('ajax/', ajax.get_up),

]
