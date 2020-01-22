from rest_framework import serializers
from rest_framework import viewsets
from api.models import *


# class CourseSerializers(serializers.ModelSerializer):
#     # one2one/fk/choice/显示单条数据
#     level = serializers.CharField(source='get_level_display')
#
#     class Meta:
#         model = Course
#         fields = '__all__'
#         depth = 2  # 显示数据深度 ************

class CourseSerializers(serializers.ModelSerializer):
    # one2one/fk/choice/显示单条数据
    level = serializers.CharField(source='get_level_display')

    class Meta:
        model = Course
        fields = ["id", "title", "level", "course_img"]


class CourseDetailSerializers(serializers.ModelSerializer):
    # m2m/多条数据
    recommend = serializers.SerializerMethodField()
    chapter_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseDetail
        fields = ["id", "why", "chapter_name", "recommend"]

    def get_recommend(self, obj):
        print(obj)
        queryset = obj.recommend.all()
        return [{'id': i.id, 'title': i.title} for i in queryset]

    def get_chapter_name(self, obj):
        ret = obj.course.chapter_set.all()
        print(ret)
        return [{'id': i.id, 'name': i.name} for i in ret]


class ChapterSerializers(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = "__all__"
