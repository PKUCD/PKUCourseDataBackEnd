from django.db import models
from user.models import User


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, null=True)
    text = models.CharField(max_length=2000, null=True)
    is_video = models.NullBooleanField(default=None)
    video = models.CharField(max_length=128, null=True)

    class Meta:
        verbose_name = '动态'
        verbose_name_plural = '动态'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=500)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    photo = models.CharField(max_length=128)

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'


class Favor(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = '点赞记录'
        verbose_name_plural = '点赞记录'


class TextKey(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    key = models.CharField(max_length=128)

    class Meta:
        verbose_name = '关键词'
        verbose_name_plural = '关键词'  
