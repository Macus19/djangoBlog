# -*-coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(u'标题',max_length=100)
    body = models.TextField(u'内容')
    # 创建时间
    created = models.DateTimeField(u'创建时间',default=timezone.now)
    updated = models.DateTimeField(u'更新时间',auto_now=True)

    # 内部类Meta，用于给model定义元数据
    class Meta:
        # ordering指定返回的数据排列顺序
        # 按时间倒序
        ordering = ('-created',)


    def __str__(self):
        return self.title