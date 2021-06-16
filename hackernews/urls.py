from django.conf.urls import url
from django.urls import path, re_path, include
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import HomePageView, NewestPageView, SubmitPageView, AskPageView, ItemPageView, CommentPageView, \
    DeletePageView, EditPageView, FomatDocPageView, PostLikeAPIToggle, UpvotedContributions, ProfilePageView, \
    TooFastView, UpvotedComments, ThreadsPageView, SubmissionsPageView, ReplyView 

# these imports are for the API 
from .api.api_views import AskViewList , AskViewDetail, UrlViewList, UrlViewDetail, \
     AskViewComments, AskViewCommentsDetail, \
     UrlViewComments, UrlViewCommentsDetail, HomeContributionsViews,\
     ProfileViewList, ProfileViewDetail, ThreadsViewDetail, PostLikeAPIToggle_api, \
    UpvotedSubmissionsAPI,UpvotedCommentsAPI, NewestContributionsView ,check_token , SubmittedAPI

api_info = openapi.Info(
    title="HackerNews API",
    default_version='v1',
    description="HackerNews API",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="contact@snippets.local"),
    license=openapi.License(name="BSD License"),
)

schema_view = get_schema_view(
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    #Under evaluation 
    # url(r'^api/login/', include('rest_social_auth.urls_jwt')),
    url(r'^api/login/', include('rest_social_auth.urls_token')),
    # url(r'^api/login/', include('rest_social_auth.urls_session')),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'api/check/', check_token),

    # url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
    
    #This is to get the an the documentacion in .yaml
    url(r'^api(?P<format>\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    #This is the API using to make automaticaly SWAGGER
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #This is using DOC
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    
    path('', HomePageView.as_view(), name='home'),  # pone '' porque es la que se abre al principio
    path('newest/', NewestPageView.as_view(), name='newest'),
    path('news/', HomePageView.as_view(), name='home_new'),
    path('submit/', SubmitPageView.as_view(), name = 'submit'),
    path('ask/', AskPageView.as_view(), name = 'ask'),
    path('item', ItemPageView.as_view(), name = 'item'),
    path('comment',CommentPageView.as_view(), name = 'comment'),
    path('edit', EditPageView.as_view(), name = 'edit'),
    path('delete-confirm', DeletePageView.as_view(), name = 'delete-confirm'),
    path('user', ProfilePageView.as_view(), name = 'user'),
    path('vote', ItemPageView.as_view(), name = 'vote'),
    path('formatdoc',FomatDocPageView.as_view(), name= 'formatdoc'),
    path('votepost/<int:id>', PostLikeAPIToggle.as_view(), name = 'votepost'),
    path('upvoted', UpvotedContributions.as_view(), name = 'upvoted'),
    path('x', TooFastView.as_view(), name='too_fast'),
    path('submitted', SubmissionsPageView.as_view(), name='submitted'),
    path('upvotedcomments', UpvotedComments.as_view(), name='upvotedcomments'),
    path('threads',ThreadsPageView.as_view(), name = 'threads'),
    path('reply', ReplyView.as_view(), name = 'reply'),
    

    # API Routes There are more specified routes in the API documentation and need to be add
    path('api/asks', AskViewList.as_view(),name='asks_list'),
    path('api/asks/<int:id>',AskViewDetail.as_view(),name = 'asks_detail'),
    path('api/asks/<int:id>/comments',AskViewComments.as_view(),name = 'asks_comments'),
    path('api/asks/<int:id>/comments/<int:commentId>',AskViewCommentsDetail.as_view(),name = 'add_asks_comments'),

    path('api/urls', UrlViewList.as_view(),name='urls_list'),
    path('api/urls/<int:id>',UrlViewDetail.as_view(),name = 'urls_detail'),
    path('api/urls/<int:id>/comments',UrlViewComments.as_view(),name = 'url_comments'),
    path('api/urls/<int:id>/comments/<int:commentId>',UrlViewCommentsDetail.as_view(),name = 'add_urls_comments'),
   
    path('api/profile/<str:username>',ProfileViewDetail.as_view(),name = 'profile_detail'),
    path('api/threads/<str:username>',ThreadsViewDetail.as_view(),name = 'profile_threads_comments'),
    path('api/contributions/<int:id>/votes', PostLikeAPIToggle_api.as_view(), name='api_votepost'),

    path('api/submitted/<str:username>', SubmittedAPI.as_view(), name='api_submitted'),
    path('api/upvotedSubmissions/<str:username>', UpvotedSubmissionsAPI.as_view(), name='api_upvotepost'),
    path('api/upvotedComments/<str:username>',UpvotedCommentsAPI.as_view(),name='api_upvotedcomments'),
    
    path('api/newest', NewestContributionsView.as_view(), name ='api_newest'),
    path('api/home', HomeContributionsViews.as_view(), name ='api_home'),

     # this is just temporal path (unnecesary)
    path('api/profile', ProfileViewList.as_view(),name='profiles_list'),
]

