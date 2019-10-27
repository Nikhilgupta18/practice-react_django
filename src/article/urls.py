from django.urls import path, reverse_lazy, re_path, include
from django.conf import settings
from .views import NewArticle, EditArticle, ReadArticle, ArticleList, ApproveArticles

urlpatterns = [

    path('', ArticleList.as_view(), name='atricle_list'),
    path('new_article/', NewArticle.as_view(), name='new_article'),
    path('approve_article/<slug:slug>/', ApproveArticles.as_view(), name='approve_article'),
    path('approve_article/', ApproveArticles.as_view(), name='approve_article'),
    path('<slug:slug>/', ReadArticle.as_view(), name='read_article'),
    path('<slug:slug>/edit/', EditArticle.as_view(), name='edit_article'),

]

if settings.DEBUG:
    urlpatterns = [


                    ] + urlpatterns

