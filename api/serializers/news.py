from rest_framework import serializers
from rest_framework import viewsets
from api.models import *


class ArticleSerializers(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ["id", "title", "brief", "head_img", "comment_num", "agree_num", "view_num", "collect_num"]


class ArticlePositionSerializers(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ["id", "title", "head_img"]


class CommentSerializers(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "content", "p_node", "agree_number", "disagree_number", 'user', 'date']