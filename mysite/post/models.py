from django.db import models
from django.db import models
from user.models import User
'''
Post:发布的data

属性：
    post_id类似于树洞的编号
    time日期
    text文本
    is_video: 多媒体内容类别,True=视频,False=图片,Null=没有多媒体内容
    video: 视频地址(可以为空)
    
外键:
    publisher: 动态发布者, user.models.User类
'''


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=2000, null=True)
    is_video = models.NullBooleanField(default=None)
    video = models.CharField(max_length=128, null=True)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '资料档案'
        verbose_name_plural = '资料档案'


'''
comment:评论类

属性：
    time：创建时间
    text：文本

外键：
    post：发布的动态
'''


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=500)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'


'''
photo:图片类

属性：
    photo：图片地址
    
外键：
    post：动态
'''


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    photo = models.CharField(max_length=128)

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'

'''
Favor:点赞记录

外键：
   post：动态
   
元数据
     unique_together: (post, user)联合唯一
'''


class Favor(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = '点赞记录'
        verbose_name_plural = '点赞记录'

'''
TextKey: 文本关键词类

属性:
    key: 文本关键词

外键:
    post: 评论动态主键, post.models.Post类
'''


class TextKey(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    key = models.CharField(max_length=128)

    class Meta:
        verbose_name = '关键词'
        verbose_name_plural = '关键词'






