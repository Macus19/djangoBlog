# -*-coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

# Create your models here.

class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    # 创建时间
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    # 文章浏览量
    total_views = models.PositiveIntegerField(default=0)

    # 内部类Meta，用于给model定义元数据
    class Meta:
        # ordering指定返回的数据排列顺序
        # 按时间倒序
        ordering = ('-created',)


    def __str__(self):
        return self.title
    
    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail',args=[self.id])