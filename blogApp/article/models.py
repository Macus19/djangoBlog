# -*-coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image

# Create your models here.
class ArticleColumn(models.Model):
    """
    栏目的Model
    """
    # 栏目标题
    title = models.CharField(max_length=100,blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章栏目的一对多外键
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    title = models.CharField(max_length=100)
    body = models.TextField()
    # 创建时间
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    # 文章浏览量
    total_views = models.PositiveIntegerField(default=0)
    # 文章标签
    tags  = TaggableManager(blank=True)
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d',blank=True)

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
    
    
    def save(self,*args,**kwargs):
        # 调用原有的save()功能
        article = super(ArticlePost,self).save(*args,**kwargs)
        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image  = Image.open(self.avatar)
            (x,y) = image.size
            new_x = 400
            new_y = int(new_x*(y/x))
            resized_image = image.resize((new_x,new_y),Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article

