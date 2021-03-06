from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import ArticlePost,ArticleColumn
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import markdown
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm

# Create your views here.
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = ArticlePost.objects.all()
    # 用户搜索逻辑
    if search:
        if order == 'total_views':
            # 用Q对象进行联合搜索
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            )
    else:
        # 
        search = ''
    
    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.update_fields(column=column)
    
    # 标签查询集
    if tag and tag !='None':
        article_list = article_list.filter(tags__name__in=[tag])
    
    # 查询集排序
    if order == 'total_view':
        article_list = ArticlePost.objects.all().order_by('-title_views')

    # 每页显示一篇文章
    paginator = Paginator(article_list,3)
    # 获取url中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给articles
    articles = paginator.get_page(page)
    # 需要传递给模板的对象
    context = {'articles':articles,
    'order':order,
    'search':search,
    'column':column,
    'tag':tag
    }
    # render函数：传递给模板，并返回对象
    return render(request,'article/list.html',context)

# 文章详情
def article_detail(request,id):
    article = ArticlePost.objects.get(id=id)
    # 取出评论
    comments = Comment.objects.filter(article=id)
    comment_form = CommentForm()
    # 浏览量加一
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        # 包含缩写、表格等常用扩展
       extensions = ['markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        # 锚点目录
        'markdown.extensions.toc'
       ])
    article.body = md.convert(article.body)
    context = {
        'article':article,
        'toc':md.toc,
        'comments':comments,
        # 引入评论表单
        'comment_form':comment_form
        }
    return render(request,'article/detail.html',context)

# 写文章的视图
def article_create(request):
    # 判断用户是否提交数据
    if request.method == 'POST':
        # 将提交的数据赋值给表单实例
        article_post_form = ArticlePostForm(request.POST,request.FILES)
        # 判断提交的数据是否满足模型的要求
        if(article_post_form.is_valid):
            # 保存数据，但不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定目前登录的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            # 保存栏目
            if request.POST['column']!='none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 文章保存到数据库中
            new_article.save()
            # 保存tags的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 获得栏目选项
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form':article_post_form,'columns':columns}
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
@login_required(login_url="/userprofile/login/")
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = { 'article': article, 
        'article_post_form': article_post_form,
        'columns' :columns,
        }
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)
