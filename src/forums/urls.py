from django.conf import settings
from django.urls import path, include, re_path
from .views import ForumView, ViewQuestion, DeleteAns, EditAns, Vote, SearchForums, AskQuestion, VoteQuestion


urlpatterns = [
    path('', ForumView.as_view(), name="forums"),
    path('ask-question/', AskQuestion.as_view(), name="ask_question"),
    path('question/<slug:ques_link>/', ViewQuestion.as_view(), name="view_question"),
    path('topics/', SearchForums.as_view(), name="search_forums"),
    # path('topics/<str:topic>', SearchForums.as_view(), name='breadcrumb'),
    path('delete-3je3q2678ui/', DeleteAns.as_view(), name='delete-ans'),
    path('edit-3je3q288iu/', EditAns.as_view(), name='edit-ans'),
    path('vote-xyzs13s44ed3/', Vote.as_view(), name='answer_page'),
    path('vote_question/', VoteQuestion.as_view(), name='vote_question'),

]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [

                    ] + urlpatterns
