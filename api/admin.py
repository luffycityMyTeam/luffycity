from django.contrib import admin

# Register your models here.
from api.models import *

admin.site.register(Course)
admin.site.register(CourseDetail)
admin.site.register(Chapter)

admin.site.register(UserInfo)

admin.site.register(ArticleSource)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Collection)
admin.site.register(PricePolicy)
admin.site.register(Coupon)
admin.site.register(CouponRecord)


