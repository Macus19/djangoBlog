# -*-coding:utf-8 -*-

from django.contrib import admin
from .models import ArticlePost,ArticleColumn
# Register your models here.
admin.site.register(ArticlePost)
admin.site.register(ArticleColumn)