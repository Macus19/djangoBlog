from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import ArticlePost
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown

# Create your views here.
def article_list(request):
    # 取出所有博客文章
    articles = ArticlePost.objects.all()
    # 需要传递给模板的对象
    context = {'articles':articles}
    # render函数：传递给模板，并返回对象
    return render(request,'article/list.html',context)

# 文章详情
def article_detail(request,id):
    article = ArticlePost.objects.get(id=id)
    article.body = markdown.markdown(article.body,
        # 包含缩写、表格等常用扩展
       extensions = ['markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite'
       ])
    context = {'article':article}
    return render(request,'article/detail.html',context)

# 写文章的视图
def article_create(request):
    # 判断用户是否提交数据
    if request.method == 'POST':
        # 将提交的数据赋值给表单实例
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if(article_post_form.is_valid):
            # 保存数据，但不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中id=1的用户为作者
            # 如果进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时要重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=1)
            # 文章保存到数据库中
            new_article.save()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文
        context = {'article_post_form':article_post_form}
        # 返回模板
        return render(request,'article/create.html',context)

# 文章删除(安全)
def article_safe_delete(request,id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

# 文章更新
def article_update(request,id):
    article = ArticlePost.objects.get(id=id)
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            return redirect("article:article_detail",article.id)
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        article_post_form = ArticlePostForm()
        context = { 'article':article,'article_post_form':article_post_form}
        return render(request,'article/update.html',context)

