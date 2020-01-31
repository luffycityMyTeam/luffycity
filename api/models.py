from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


# Create your models here.


class Course(models.Model):
    title = models.CharField(max_length=32, verbose_name="课程名称")
    course_img = models.CharField(default="/static/course_img/default.png", max_length=128, verbose_name="课程图片")
    rank = (
        (1, "初级"),
        (2, "中级"),
        (3, "高级"),
    )
    level = models.IntegerField(choices=rank, default=1, verbose_name="课程难度")
    course_detail = models.OneToOneField(to="CourseDetail", on_delete=models.CASCADE, verbose_name="课程详情")

    policy_list = GenericRelation(to="PricePolicy")
    coupon_list = GenericRelation(to="Coupon")

    def __str__(self):
        return self.title


class CourseDetail(models.Model):
    why = models.CharField(max_length=128, verbose_name="为什么学")
    recommend = models.ManyToManyField(to="Course", verbose_name="推荐课程", related_name='rm')

    def __str__(self):
        return '为什么学:{}'.format(self.why)


class Chapter(models.Model):
    name = models.CharField(max_length=128, verbose_name="章节名称")
    courseChapter = models.ForeignKey(to="Course", on_delete=models.CASCADE, verbose_name="关联课程")

    def __str__(self):
        return "章节名称: %s" % self.name


class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    pwd = models.CharField(max_length=64)

    def __str__(self):
        return self.username


class UserToken(models.Model):
    user = models.OneToOneField(to="UserInfo", on_delete=models.CASCADE)
    token = models.CharField(max_length=128)


# #################  深科技 ############################
class ArticleSource(models.Model):
    '''文章来源'''
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = '16.文章来源'

    def __str__(self):
        return self.name


class Article(models.Model):
    """文章资讯"""
    title = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="标题")
    source = models.ForeignKey(to="ArticleSource", verbose_name="来源", on_delete=models.CASCADE)
    article_type_choices = ((0, '资讯'), (1, '视频'))
    article_type = models.SmallIntegerField(choices=article_type_choices, default=0)
    brief = models.TextField(max_length=512, verbose_name="摘要")
    head_img = models.CharField(max_length=255)
    content = models.TextField(verbose_name="文章正文")
    pub_date = models.DateTimeField(verbose_name="上架日期")
    offline_date = models.DateTimeField(verbose_name="下架日期")
    status_choices = ((0, '上线'), (1, "下线"))
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name='状态')
    order = models.SmallIntegerField(default=0, verbose_name='权重', help_text="文章想置顶,可以吧数字调大")
    vid = models.CharField(max_length=128, verbose_name="视频vid", help_text="文章类型是视频,则需要添加视频Vid")
    comment_num = models.SmallIntegerField(default=0, verbose_name='评论数')
    agree_num = models.SmallIntegerField(default=0, verbose_name='点赞数')
    view_num = models.SmallIntegerField(default=0, verbose_name='观看数')
    collect_num = models.SmallIntegerField(default=0, verbose_name='收藏数')

    date = models.DateTimeField(auto_now_add=True, verbose_name='创建时期')
    position_choices = ((0, '信息流'), (1, 'banner大图'), (2, 'banner小图'))
    position = models.SmallIntegerField(choices=position_choices, default=0, verbose_name="位置")

    comment = GenericRelation('Comment')

    class Meta:
        verbose_name_plural = '17.文章'

    def __str__(self):
        return '{}-{}'.format(self.source, self.title)


class Collection(models.Model):
    '''收藏'''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("content_type", 'object_id', 'user')  # 联合唯一
        verbose_name_plural = "18.通用收藏表"


class Comment(models.Model):
    """通用评论表"""
    content_type = models.ForeignKey(ContentType, blank=True, null=True, verbose_name="类型", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    p_node = models.ForeignKey("self", blank=True, null=True, verbose_name="父级评论", on_delete=models.CASCADE)
    content = models.TextField(max_length=1024)
    user = models.ForeignKey("UserInfo", verbose_name="会员名", on_delete=models.CASCADE)
    disagree_number = models.IntegerField(default=0, verbose_name="踩数")
    agree_number = models.IntegerField(default=0, verbose_name="赞同数")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = "19.通用评论表"


class PricePolicy(models.Model):
    '''价格策略'''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    # 不会在数据库中生成列,只用于帮助你进行添加和查询
    content_object = GenericForeignKey('content_type', 'object_id')
    price = models.CharField(default=99, verbose_name='价格', max_length=64)
    date_choice = ((30, '一个月'), (90, '3个月'), (180, '6个月'), (240, '8个月'), (365, '1年'))
    policy = models.SmallIntegerField(choices=date_choice, verbose_name='时间')

    class Meta:
        verbose_name_plural = '价格策略'

    def __str__(self):
        return '(%s)(%s)(%s元)' % (self.content_object, self.get_policy_display(), self.price)


# ######################## 优惠券 ##########################
class Coupon(models.Model):
    """优惠劵生成规则, 运营人员添加"""
    name = models.CharField(max_length=64, verbose_name="活动名称")
    brief = models.TextField(blank=True, null=True, verbose_name="优惠券介绍")
    coupon_type_choices = ((0, "立减券"), (1, "满减券"), (2, "折扣券"))
    coupon_type = models.SmallIntegerField(choices=coupon_type_choices, default=0, verbose_name="券类型")
    """
    立减：
        money_equivalent_value = 100 (减100元)
                   off_percent = null
               minimum_consume = 0   (最低0元可用)
    满减：
        money_equivalent_value = 100 (减100元)
                   off_percent = null
               minimum_consume = 500 (满500元可用)
    折扣：
        money_equivalent_value = 0
                   off_percent = 79  (打7.9折)
               minimum_consume = 300 (满300元可用)           
    """
    money_equivalent_value = models.IntegerField(verbose_name="等值货币")
    off_percent = models.PositiveSmallIntegerField("折扣百分比", help_text="只针对折扣券,例7.9折，写79", blank=True, null=True)
    minimum_consume = models.PositiveIntegerField("最低消费", default=0, help_text="仅在满减券时填写此字段")

    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField("绑定课程", blank=True, null=True, help_text="可以把优惠券跟课程绑定")
    content_object = GenericForeignKey("content_type", "object_id")

    quantity = models.PositiveIntegerField("数量(张)", default=1)
    open_date = models.DateField("优惠券领取开始时间")
    close_date = models.DateField("优惠券领取结束时间")
    valid_begin_date = models.DateField(verbose_name="有效期开始时间", blank=True, null=True)
    valid_end_date = models.DateField(verbose_name="有效期结束时间", blank=True, null=True)
    coupon_valid_days = models.PositiveIntegerField(verbose_name="优惠券有效期(天)", blank=True, null=True,
                                                    help_text="自券被领时开始算起")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "31.优惠劵生成记录"

    def __str__(self):
        return "%s(%s)" % (self.get_coupon_type_display(), self.name)


class CouponRecord(models.Model):
    """优惠卷发放、消费记录"""
    coupon = models.ForeignKey("Coupon", on_delete=models.CASCADE)
    number = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey("UserInfo", verbose_name="拥有者", on_delete=models.CASCADE)
    status_choices = ((0, '未使用'), (1, '已使用'), (2, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    get_time = models.DateTimeField(verbose_name="领取时间", help_text="用户领取时间")
    used_time = models.DateTimeField(blank=True, null=True, verbose_name="使用时间")
    # order = models.ForeignKey("Order", blank=True, null=True, verbose_name="关联订单",
    #                           on_delete=models.CASCADE)  # 一个订单可以有多个优惠券

    class Meta:
        verbose_name_plural = "32.用户优惠券"

    def __str__(self):
        return '%s-%s-%s' % (self.user, self.number, self.get_status_display())