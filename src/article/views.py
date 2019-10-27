from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ArticleForm
from inv.settings import enable_otp
from .models import Article
from django.contrib import messages
from account.tasks import send_email
from django.shortcuts import redirect
from django.db.models import Q


class NewArticle(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        is_publisher = user.student.publisher

        if not is_publisher:
            return render(request, template_name='error.html', context={})

        context = dict()
        context['form'] = ArticleForm

        return render(request, template_name='article/article.html', context=context)

    def post(self, request, *args, **kwargs):

        user = request.user
        is_publisher = user.student.publisher

        if not is_publisher:
            return render(request, template_name='error.html', context={})

        context = dict()
        context['form'] = ArticleForm

        title = request.POST.get('title')
        content = request.POST.get('content')

        slug = slugify(title)
        slug = slug[:128]

        if Article.objects.filter(title=title).exists():
            messages.error(request, "Could not publish article. A Similar Article Already Exists.")
            context['form'] = ArticleForm({'content': content, 'title': title})
            return render(request, template_name='article/article.html', context=context)

        Article.objects.create(author=request.user, title=title, content=content, slug=slug)
        messages.success(request, "The article has been saved and is now in review. As soon as it is published, we will send you an email.")

        if enable_otp:
            send_email.delay(receiver=["mittrayash@gmail.com"], email_message="New Article to be approved.", subject="New article to be approved!<br><br>" + title)
        else:
            print("Not sending email because in development mode.")

        return render(request, template_name='article/article.html', context=context)


class EditArticle(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user
        is_publisher = user.student.publisher

        if not is_publisher:
            return render(request, template_name='error.html', context={})

        slug = kwargs.get('slug')
        if not Article.objects.filter(slug__iexact=slug).exists():
            messages.error(request, "No such article found.")
            return render(request, template_name='error.html', context={})
        else:
            article = Article.objects.filter(slug__iexact=slug).first()

        if not article.author == user:
            messages.error(request, "You do not own this article.")
            return render(request, template_name='error.html', context={})

        context = dict()
        context['form'] = ArticleForm({'content': article.content, 'title': article.title})
        context['title'] = article.title
        context['content'] = article.content
        context['edit'] = True
        context['slug'] = slug

        return render(request, template_name='article/article.html', context=context)

    def post(self, request, *args, **kwargs):

        user = request.user
        is_publisher = user.student.publisher

        if not is_publisher:
            return render(request, template_name='error.html', context={})

        slug = kwargs.get('slug')
        if not Article.objects.filter(slug__iexact=slug).exists():
            messages.error(request, "No such article found.")
            return render(request, template_name='error.html', context={})
        else:
            article = Article.objects.filter(slug__iexact=slug).first()

        if not article.author == user:
            messages.error(request, "You do not own this article.")
            return render(request, template_name='error.html', context={})

        context = dict()
        context['form'] = ArticleForm
        title = request.POST.get('title')
        content = request.POST.get('content')

        article.title = title
        article.content = content
        article.save()

        if enable_otp:
            send_email.delay(receiver=["mittrayash@gmail.com"], email_message="New Article to be approved.<br><br>" + title,
                             subject="Article edited!")
        else:
            print("Not sending email because in development mode.")

        messages.success(request, "Successfully Edited Article.")

        return redirect('/article/new_article/')


class ReadArticle(View):

    def get(self, request, *args, **kwargs):
        user = request.user

        slug = kwargs.get('slug')
        if not Article.objects.filter(slug__iexact=slug).exists():
            messages.error(request, "No such article found.")
            return render(request, template_name='error.html', context={})
        else:
            article = Article.objects.filter(slug__iexact=slug).first()

        if article.status == 'in_review':
            if user != article.author and not user.is_superuser:
                messages.warning(request, "This article is still in review. It will be available for reading once approved.")
                return render(request, template_name='error.html', context={})
            else:
                messages.warning(request, "This article is still in review. Only you can see this until it is approved.")
                context = dict()
                context['article'] = article
                return render(request, template_name='article/read_article.html', context=context)

        if not article.author == user:
            article.no_of_views += 1
            article.save()

        context = dict()
        context['article'] = article

        return render(request, template_name='article/read_article.html', context=context)


class ArticleList(View):
    def get(self, request, *args, **kwargs):

        context = dict()
        articles = Article.objects.filter(status='approved').order_by('-timestamp')
        context['articles'] = articles

        return render(request, template_name='article/article_list.html', context=context)


class ApproveArticles(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'error.html', context={})

        context = dict()
        articles = Article.objects.filter(~Q(status='approved')).order_by('-timestamp')
        context['articles'] = articles

        return render(request, template_name='article/approve_articles.html', context=context)

    def post(self, request, *args, **kwargs):

        slug = kwargs.get('slug')

        if not request.user.is_superuser:
            return render(request, 'error.html', context={})

        article = Article.objects.filter(slug=slug).first()
        if not article:
            messages.warning(request, "Article not found.")
            return render(request, 'error.html', context={})

        article.status = 'approved'
        article.save()

        author_email = article.author.email

        subject = "Your article has been approved on YMGrad.com"
        msg = "Congratulations! Your article titled '" + article.title + "' is now live. Anyone who visits YMGrad can now see it!<br><br>Best Regards,<br>The YMGrad Team"

        if enable_otp:
            send_email.delay(receiver=[author_email], email_message=msg, subject=subject)
        else:
            print("Not sending email because in development mode.")

        context = dict()
        articles = Article.objects.filter(~Q(status='approved')).order_by('-timestamp')
        context['articles'] = articles

        return render(request, template_name='article/approve_articles.html', context=context)
