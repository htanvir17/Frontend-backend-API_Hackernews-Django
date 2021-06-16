from rest_framework import generics

from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.forms.models import model_to_dict

from itertools import chain
from operator import attrgetter

from django.contrib.auth.models import User
from datetime import datetime, timedelta

# In evaluation
from rest_framework import authentication, permissions

from django.shortcuts import render, get_object_or_404
# In evaluation
from django.http import JsonResponse
from rest_framework import status
from django.http import Http404
from django.db import IntegrityError
from django.db.models import Count

import json

# API Key
# from rest_framework_api_key.permissions import HasAPIKey
# from rest_framework.permissions import IsAuthenticated

from ..models import Contribution, ContributionUrl, ContributionAsk, ContributionComment, UserProfile, User

# for serializers
from drf_multiple_model.views import ObjectMultipleModelAPIView
# to send data in file api_serializers to manipulate data
from .api_serializers import ContributionAskSerializer, ContributionUrlSerializer, ContributionReplySerializer, \
    ContributionCommentSerializer, ProfileSerializer, CommentsThreadsSerializer, ContributionUrlAskSerializer

# from rest_framework_api_key.models import AbstractAPIKey
# from rest_framework_api_key.admin import APIKey

###UNDER EVALUATION
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from rest_framework.authtoken.models import Token

## testing
@csrf_exempt
@api_view(['POST'])
def check_token(request, format=None):
    token = Token.objects.filter(key=request.data['token']).exists()
    return JsonResponse({"status": token})


## function thar check user credential
def get_global_evaluation(request):
    try:
        api_key = request.META["HTTP_AUTHORIZATION"]
    except:
        return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                        status=status.HTTP_401_UNAUTHORIZED)

    user_sended = UserProfile.objects.filter(apikey=api_key)

    if not api_key or not user_sended:
        return Response(
            {"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
            status=status.HTTP_401_UNAUTHORIZED)
    return None



## the class APIView is not necessary for us, but we use to show the data in a nice way in browser 
class AskViewList(APIView):
    def get(self, request):
        evaluation = get_global_evaluation(request)
        # i think is unnecesary to check because if all goes fine then evalution will have None, other hand will give return
        if evaluation:
            return evaluation
        asks = ContributionAsk.objects.all().order_by('-creation_date')
        self.queryset = ContributionAskSerializer(asks, many=True).data #this 'data' is a variable of ContributionAskSerializer class
        return Response(self.queryset, status=status.HTTP_200_OK)

    # when user want to post an ask via API
    def post(self, request):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        author_sended = UserProfile.objects.filter(apikey=api_key)
        if not api_key or not author_sended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        title = request.data['title']
        text = request.data['text']
        message = ''
        if len(title) == 0:
            message = 'Title can not be empty'
        elif len(title) > 80:
            message = 'Title is too long (maximum 80 characters)'

        if len(text) > 500:
            if message:
                message = message + " - "
            message = message + 'Text is too long (maximum 500 characters)'
        
        if message: #it means that violate some RT
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        
        # we store the contribution in DB
        new_ask = ContributionAsk(title=title, text=text, creation_date=datetime.now(), author=author_sended[0].user)
        new_ask.save()

        new_ask_serialized = ContributionAskSerializer(new_ask).data
        return Response(new_ask_serialized, status=status.HTTP_201_CREATED)



class AskViewDetail(APIView):
    
    # called by put() & delete()
    def evaluation(self, request, id):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        author_sended = UserProfile.objects.filter(apikey=api_key)
        if not api_key or not author_sended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        ask = ContributionAsk.objects.filter(id_contribution=id)
        if not ask:
            return Response({"error": "No contribution with that ID"}, status=status.HTTP_404_NOT_FOUND)

        if author_sended[0].user != ask[0].author:
            return Response({"error": "Your api key (X-API-KEY Header) is not valid to do this request"},
                            status=status.HTTP_403_FORBIDDEN)
        return None

    def get(self, request, id):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        ask = ContributionAsk.objects.filter(id_contribution=id)
        if not ask:
            return Response({"error": "No ContributionAsk with that ID"}, status=status.HTTP_404_NOT_FOUND)
        
        contribution = ask[0]
        Contribution_serialized = {
            'id_contribution': contribution.id_contribution,
            'title': contribution.title,
            'creation_date': contribution.creation_date,
            'text': contribution.text,
            'author': contribution.author.username,
            'points': contribution.getpoints()
        }
        #get comments of this ask
        commentlist = ContributionComment.objects.filter(contribution_ref=contribution, parent=None)
        CommentsThreadsSerializedList = []
        for comment in commentlist:
            CommentsThreadsSerializedList.append(CommentsThreadsSerializer().data(comment))
        Contribution_serialized['comments'] = CommentsThreadsSerializedList
        # print(Contribution_serialized)
        return Response(Contribution_serialized, status=status.HTTP_200_OK)

    def put(self, request, id):
        result = self.evaluation(request, id)
        if result:
            return result
        title = request.data['title']
        text = request.data['text']
        message = ''
        if len(title) == 0:
            message = 'Title can not be empty'
        elif len(title) > 80:
            message = 'Title is too long (maximum 80 characters)'
        if message:
            message = message + " - "
        if len(text) > 500:
            message = message + 'Text is too long (maximum 500 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ContributionAsk.objects.filter(id_contribution=id).update(title=title, text=text)
            return Response("Modified", status=status.HTTP_200_OK)

    def delete(self, request, id):
        result = self.evaluation(request, id)
        if result:
            return result
        ContributionAsk.objects.filter(id_contribution=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class UrlViewList(APIView):
    def get(self, request):
        evaluation = get_global_evaluation(request)
        if evaluation:
            return evaluation
        urls = asks = ContributionUrl.objects.all().order_by('-creation_date')
        self.queryset = ContributionUrlSerializer(urls, many=True).data
        return Response(self.queryset, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        author_sended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not author_sended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        title = request.data['title']
        url = request.data['url']

        message = ''
        if len(title) == 0:
            message = 'Title can not be empty'
        elif len(title) > 80:
            message = 'Title is too long (maximum 80 characters)'
        if len(url) == 0:
            if message:
                message = message + " - "
            message = message + "Url can not be empty"

        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_url = ContributionUrl(title=title, url=url, creation_date=datetime.now(), author=author_sended[0].user)
            new_url.save()
            new_url_serialized = ContributionUrlSerializer(new_url).data
            return Response(new_url_serialized, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in e.args[0]:
                url_existent = ContributionUrl.objects.filter(url=url)
                url = get_object_or_404(ContributionUrl, id_contribution=url_existent[0].id_contribution)
                data = ContributionUrlSerializer(url).data
                return Response({"error": "Url already exists", "contribution": data}, status=status.HTTP_409_CONFLICT)



class UrlViewDetail(APIView):
    def evaluation(self, request, id):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        author_sended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not author_sended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        url = ContributionUrl.objects.filter(id_contribution=id)
        if not url:
            return Response({"error": "No contribution with that ID"}, status=status.HTTP_404_NOT_FOUND)

        if author_sended[0].user != url[0].author:
            return Response({"error": "Your api key (X-API-KEY Header) is not valid to do this request"},
                            status=status.HTTP_403_FORBIDDEN)

    def get(self, request, id):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        url = ContributionUrl.objects.filter(id_contribution=id)
        if not url:
            return Response({"error": "No ContributionUrl with that ID"}, status=status.HTTP_404_NOT_FOUND)
        contribution = url[0]
        Contribution_serialized = {
            'id_contribution': contribution.id_contribution,
            'creation_date': contribution.creation_date,
            'title': contribution.title,
            'url': contribution.url,
            'author': contribution.author.id,
            'points': contribution.getpoints()
        }
        commentlist = ContributionComment.objects.filter(contribution_ref=contribution, parent=None)
        CommentsThreadsSerializedList = []
        for comment in commentlist:
            CommentsThreadsSerializedList.append(CommentsThreadsSerializer().data(comment))
        Contribution_serialized['comments'] = CommentsThreadsSerializedList
        # print(Contribution_serialized)
        return Response(Contribution_serialized, status=status.HTTP_200_OK)

    def put(self, request, id):
        result = self.evaluation(request, id)
        if result:
            return result
        title = request.data['title']
        message = ''
        if len(title) == 0:
            message = 'Title can not be empty'
        elif len(title) > 80:
            message = 'Title is too long (maximum 80 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ContributionUrl.objects.filter(id_contribution=id).update(title=title)
            return Response("Modified", status=status.HTTP_200_OK)

    def delete(self, request, id):
        result = self.evaluation(request, id)
        if result:
            return result
        ContributionUrl.objects.filter(id_contribution=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AskViewComments(APIView):
    def get(self, request, id):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        ask = ContributionAsk.objects.filter(id_contribution=id)
        if not ask:
            return Response({"error": "No ContributionAsk with that ID"}, status=status.HTTP_404_NOT_FOUND)
        
        commentlist = ContributionComment.objects.filter(contribution_ref=id, parent=None)
        CommentsThreadsSerializedList = []
        for comment in commentlist:
            CommentsThreadsSerializedList.append(CommentsThreadsSerializer().data(comment))
        return Response(CommentsThreadsSerializedList, status=status.HTTP_200_OK)

    def post(self, request, id):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        author_sended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not author_sended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        ask = ContributionAsk.objects.filter(id_contribution=id)
        if not ask:
            return Response({"error": "No ContributionAsk with that ID"}, status=status.HTTP_404_NOT_FOUND)
        text = request.data['text']
        contribution_root = ask

        if contribution_root[0].author.id == author_sended[0].id:
            return Response({"error": "You can't comment your own Contribution"}, status=status.HTTP_403_FORBIDDEN)
        message = ''
        if len(text) == 0:
            message = 'text can not be empty'
        if len(text) > 500:
            message = message + 'Text is too long (maximum 500 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        author_comment = User.objects.filter(id=author_sended[0].id)
        new_comment = ContributionComment(text=text, creation_date=datetime.now(), author=author_comment[0],
                                          contribution_ref=contribution_root[0])
        new_comment.save()
        n_coments = contribution_root[0].comments + 1
        contribution_root.update(comments=n_coments)
        new_comment_serialized = ContributionCommentSerializer(new_comment).data
        return Response(new_comment_serialized, status=status.HTTP_201_CREATED)



class AskViewCommentsDetail(APIView):
    
    def reviewer(self, request, id, comment, auth_needed):
        ask = ContributionAsk.objects.filter(id_contribution=id)

        if not ask:
            return Response({"error": "No ContributionAsk with that ID"}, status=status.HTTP_404_NOT_FOUND)

        if not comment:
            return Response({"error": "No ContributionComment with that commentId"}, status=status.HTTP_404_NOT_FOUND)

        if comment[0].contribution_ref.id_contribution != id:
            a = str(comment[0].id_contribution)
            b = str(id)
            return Response({
                "error": "The contributionComment(commentID=" + a + ") isn't a comment of the Contribution(ID=" + b + ")"},
                status=status.HTTP_400_BAD_REQUEST)
        api_key = request.META["HTTP_AUTHORIZATION"]
        author_sended = UserProfile.objects.filter(apikey = api_key)        
        if auth_needed and author_sended[0].user.id != comment[0].author.id:
            return Response({"error": "Your api key (X-API-KEY Header) is not valid to do this request"},
                            status=status.HTTP_403_FORBIDDEN)
        return None

    def get(self, request, id, commentId):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        comment = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, comment, False)
        if review:
            return review
        commentSerialized = CommentsThreadsSerializer().data(comment[0])
        return Response(commentSerialized, status=status.HTTP_200_OK)
    
    def post(self, request, id, commentId):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        parent = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, parent, False)
        if review:
            return review
        
        api_key = request.META["HTTP_AUTHORIZATION"]
        author_sended = UserProfile.objects.filter(apikey=api_key)
        if parent[0].author.id == author_sended[0].id:
            return Response({"error": "You can't reply your own Comment"}, status=status.HTTP_403_FORBIDDEN)
        text = request.data['text']
        message = ''
        if len(text) == 0:
            message = 'text can not be empty'
        if len(text) > 500:
            message = message + 'Text is too long (maximum 500 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        author_comment = User.objects.filter(id=author_sended[0].id)
        new_reply = ContributionComment(text=text, creation_date=datetime.now(), author=author_comment[0],
                                        contribution_ref=parent[0].contribution_ref, parent=parent[0])
        new_reply.save()
        contribution_root = Contribution.objects.filter(id_contribution=parent[0].contribution_ref.id_contribution)
        n_coments = contribution_root[0].comments + 1
        contribution_root.update(comments=n_coments)
        new_reply_serialized = ContributionReplySerializer(new_reply).data
        return Response(new_reply_serialized, status=status.HTTP_201_CREATED)
    
    def put(self, request, id, commentId):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        comment = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, comment, True)
        if review:
            return review
        text = request.data['text']
        message = ''
        if len(text) == 0:
            message = 'text can not be empty'
        elif len(text) > 80:
            message = message + 'Text is too long (maximum 500 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            comment.update(text=text)
            return Response("Modified", status=status.HTTP_200_OK)

    def delete(self, request, id, commentId):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        comment = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, comment, True)
        if review:
            return review
        contribution_root = comment[0].contribution_ref
        comment.delete()
        n_coments = contribution_root.comments - 1
        Contribution.objects.filter(id_contribution=contribution_root.id_contribution).update(comments=n_coments)
        return Response(status=status.HTTP_204_NO_CONTENT)



class UrlViewComments(APIView):
    def get(self, request, id):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        url = ContributionUrl.objects.filter(id_contribution=id)
        if not url:
            return Response({"error": "No ContributionUrl with that ID"}, status=status.HTTP_404_NOT_FOUND)
        commentlist = ContributionComment.objects.filter(contribution_ref=id, parent=None)
        CommentsThreadsSerializedList = []
        for comment in commentlist:
            CommentsThreadsSerializedList.append(CommentsThreadsSerializer().data(comment))
        return Response(CommentsThreadsSerializedList, status=status.HTTP_200_OK)

    def post(self, request, id):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        author_sended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not author_sended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        url = ContributionUrl.objects.filter(id_contribution=id)
        if not url:
            return Response({"error": "No ContributionUrl with that ID"}, status=status.HTTP_404_NOT_FOUND)
        text = request.data['text']
        contribution_root = url

        if contribution_root[0].author.id == author_sended[0].id:
            return Response({"error": "You can't comment your own Contribution"}, status=status.HTTP_403_FORBIDDEN)
        message = ''
        if len(text) == 0:
            message = 'text can not be empty'
        if len(text) > 500:
            message = message + 'Text is too long (maximum 500 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        author_comment = User.objects.filter(id=author_sended[0].id)
        new_comment = ContributionComment(text=text, creation_date=datetime.now(), author=author_comment[0],
                                          contribution_ref=contribution_root[0])
        new_comment.save()
        n_coments = contribution_root[0].comments + 1
        contribution_root.update(comments=n_coments)
        new_comment_serialized = ContributionCommentSerializer(new_comment).data
        return Response(new_comment_serialized, status=status.HTTP_201_CREATED)



class UrlViewCommentsDetail(APIView):

    def reviewer(self, request, id, comment, auth_needed):
        url = ContributionUrl.objects.filter(id_contribution=id)

        if not url:
            return Response({"error": "No ContributionUrl with that ID"}, status=status.HTTP_404_NOT_FOUND)

        if not comment:
            return Response({"error": "No ContributionComment with that commentId"}, status=status.HTTP_404_NOT_FOUND)
        

        if comment[0].contribution_ref.id_contribution != id:
            a = str(comment[0].id_contribution)
            b = str(id)
            return Response({
                "error": "The contributionComment(commentID=" + a + ") isn't a comment of the Contribution(ID=" + b + ")"},
                status=status.HTTP_400_BAD_REQUEST)
        
        api_key = request.META["HTTP_AUTHORIZATION"]
        author_sended = UserProfile.objects.filter(apikey = api_key)
        if auth_needed and author_sended[0].user.id != comment[0].author.id:
            return Response({"error": "Your api key (X-API-KEY Header) is not valid to do this request"},
                            status=status.HTTP_403_FORBIDDEN)
        return None

    def get(self, request, id, commentId):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        comment = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, comment, False)
        if review:
            return review
        commentSerialized = CommentsThreadsSerializer().data(comment[0])
        return Response(commentSerialized, status=status.HTTP_200_OK)

    def post(self, request, id, commentId):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        parent = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, parent, False)
        if review:
            return review
        api_key = request.META["HTTP_AUTHORIZATION"]
        author_sended = UserProfile.objects.filter(apikey=api_key)
        if parent[0].author.id == author_sended[0].id:
            return Response({"error": "You can't reply your own Comment"}, status=status.HTTP_403_FORBIDDEN)
        text = request.data['text']
        message = ''
        if len(text) == 0:
            message = 'text can not be empty'
        if len(text) > 500:
            message = message + 'Text is too long (maximum 500 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        author_comment = User.objects.filter(id=author_sended[0].id)
        new_reply = ContributionComment(text=text, creation_date=datetime.now(), author=author_comment[0],
                                        contribution_ref=parent[0].contribution_ref, parent=parent[0])
        new_reply.save()
        contribution_root = Contribution.objects.filter(id_contribution=parent[0].contribution_ref.id_contribution)
        n_coments = contribution_root[0].comments + 1
        contribution_root.update(comments=n_coments)
        new_reply_serialized = ContributionReplySerializer(new_reply).data
        return Response(new_reply_serialized, status=status.HTTP_201_CREATED)
        
    def put(self, request, id, commentId):
        comment = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, comment, True)
        if review:
            return review
        text = request.data['text']
        message = ''
        if len(text) == 0:
            message = 'text can not be empty'
        elif len(text) > 80:
            message = message + 'Text is too long (maximum 500 characters)'
        if message:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            comment.update(text=text)
            return Response("Modified", status=status.HTTP_200_OK)

    def delete(self, request, id, commentId):
        comment = ContributionComment.objects.filter(id_contribution=commentId)
        review = self.reviewer(request, id, comment, True)
        if review:
            return review
        contribution_root = comment[0].contribution_ref
        comment.delete()
        n_coments = contribution_root.comments - 1
        Contribution.objects.filter(id_contribution=contribution_root.id_contribution).update(comments=n_coments)
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProfileViewList(APIView):

    def get(self, request):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        profiles = UserProfile.objects.all()
        data = ProfileSerializer().data(profiles)
        return Response(data, status=status.HTTP_200_OK)

class ProfileViewDetail(APIView):

    def evaluation(self, request, user):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user_sended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not user_sended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user:
            return Response({"error": "No Profile with that username"}, status=status.HTTP_404_NOT_FOUND)
        if user_sended[0].user.id != user[0].id:
            return Response({"error": "Your api key (X-API-KEY Header) is not valid to do this request"},
                            status=status.HTTP_403_FORBIDDEN)
        return None

    def get(self, request, username):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        user = User.objects.filter(username=username)
        if not user:
            return Response({"error": "No Profile with that username"}, status=status.HTTP_404_NOT_FOUND)
        userProfile = UserProfile.objects.filter(user=user[0])
        data = ProfileSerializer().data(userProfile)
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, username):
        user = User.objects.filter(username=username)
        result = self.evaluation(request, user)
        if result:
            return result
        about = request.data['about']
        message = ''
        if len(about) > 500:
            message = 'Text is too long (maximum 500 characters)'
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            UserProfile.objects.filter(user=user[0]).update(about=about)
            return Response("Modified", status=status.HTTP_200_OK)



class ThreadsViewDetail(APIView):
    def get(self, request, username):
        eval_get = get_global_evaluation(request)
        if eval_get:
            return eval_get
        user = User.objects.filter(username=username)
        if not user:
            return Response({"error": "No Profile with that username"}, status=status.HTTP_404_NOT_FOUND)
        
        commentlist = ContributionComment.objects.filter(author=user[0])
        CommentsThreadsSerializedList = []
        for comment in commentlist:
            CommentsThreadsSerializedList.append(CommentsThreadsSerializer().data(comment))
        
        return Response(CommentsThreadsSerializedList, status=status.HTTP_200_OK)



class PostLikeAPIToggle_api(APIView):

    def evaluation(self, request, id):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user_sended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not user_sended:
            return Response(
                {"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                status=status.HTTP_401_UNAUTHORIZED)

        contribution = Contribution.objects.filter(id_contribution=id)
        if not contribution:
            return Response({"error": "No Contribution with that ID"}, status=status.HTTP_404_NOT_FOUND)

        if user_sended[0].user == contribution[0].author:
            return Response({"error": "You can't vote your own Contribution"},
                            status=status.HTTP_403_FORBIDDEN)
        return None

    def evaluation_delete(self, request, id):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user_sended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not user_sended:
            return Response(
                {"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                status=status.HTTP_401_UNAUTHORIZED)

        contribution = Contribution.objects.filter(id_contribution=id)
        if not contribution:
            return Response({"error": "No Contribution with that ID"}, status=status.HTTP_404_NOT_FOUND)

        if user_sended not in contribution[0].points:
            return Response({"error": "You did not vote this contribution. Therefore, you cannot unvote"},
                            status=status.HTTP_409_CONFLICT)

        return None

    def put(self, request, id=None):

        obj = get_object_or_404(Contribution, pk=id)
        url_ = obj.get_absolute_url()
        user = self.request.user
        updated = False
        liked = False

        if user.is_authenticated:
            if user in obj.points.all():
                liked = False
                obj.points.remove(user)
            else:
                liked = True
                obj.points.add(user)
            updated = True
        data = {
            "updated": updated,
            "liked": liked,
            "points": obj.points.count()
        }
        return Response(data)

    def post(self, request, id):
        result = self.evaluation(request, id)

        if result:
            return result

        obj = get_object_or_404(Contribution, pk=id)

        api_key = request.META["HTTP_AUTHORIZATION"]
        user = UserProfile.objects.filter(apikey=api_key)[0].user
        updated = False
        liked = False

        if user in obj.points.all():
            # liked = False
            # obj.points.remove(user)
            return Response({"error": "You have already voted this contribution"},
                            status=status.HTTP_409_CONFLICT)
        else:
            liked = True
            obj.points.add(user)

        updated = True
        data = {
            "updated": updated,
            "liked": liked,
            "points": obj.points.count()
        }
        return Response("Vote created", status=status.HTTP_201_CREATED)

    def delete(self, request, id):

        result = self.evaluation(request, id)

        if result:
            return result

        obj = get_object_or_404(Contribution, pk=id)

        api_key = request.META["HTTP_AUTHORIZATION"]
        user = UserProfile.objects.filter(apikey=api_key)[0].user
        updated = False
        liked = False

        if user in obj.points.all():
            liked = False
            obj.points.remove(user)

        updated = True

        data = {
            "updated": updated,
            "liked": liked,
            "points": obj.points.count()
        }
        return Response(status=status.HTTP_204_NO_CONTENT)



class UpvotedSubmissionsAPI(APIView):
    def get(self, request, username):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        usersended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not usersended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(username=username)
        if not user:
            return Response({"error": 'No User with that username'}, status=status.HTTP_404_NOT_FOUND)
        usernameProfile = UserProfile.objects.filter(user=user[0].id)
        if usernameProfile is usersended:
            return Response(status=status.HTTP_403_FORBIDDEN)

        contribution = Contribution.objects.filter(points=user[0]).order_by('-points')

        print(contribution)
        data = ContributionUrlAskSerializer(contribution).data
        return Response(data, status=status.HTTP_200_OK)



class UpvotedCommentsAPI(APIView):
    def get(self, request, username):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        usersended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not usersended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(username=username)
        if not user:
            return Response({"error": 'No User with that username'}, status=status.HTTP_404_NOT_FOUND)
        usernameProfile = UserProfile.objects.filter(user=user[0].id)
        if usernameProfile is usersended:
            return Response(status=status.HTTP_403_FORBIDDEN)
        upvotedcomments  = ContributionComment.objects.filter(points=user[0]).order_by('-creation_date')
        serialized_upvotedcomments = []
        for comment in upvotedcomments: 
            if comment.parent is None:
                s = ContributionCommentSerializer(comment,many=False).data
            else:
                s = ContributionReplySerializer(comment,many=False).data
            s['contribution_ref_title'] = comment.contribution_ref.get_short_title()
            serialized_upvotedcomments.append(s)
        return Response(serialized_upvotedcomments, status=status.HTTP_200_OK)



class NewestContributionsView(APIView):
    def get(self, request):
        evaluation = get_global_evaluation(request)
        if evaluation:
            return evaluation
        a = ContributionUrl.objects.all()
        b = ContributionAsk.objects.all()
        result = sorted(chain(a, b), key=attrgetter('creation_date'), reverse=True)
        self.queryset = ContributionUrlAskSerializer(result).data
        return Response(self.queryset, status=status.HTTP_200_OK)



class HomeContributionsViews(APIView):
    def get(self, request):
        evaluation = get_global_evaluation(request)
        if evaluation:
            return evaluation
        a = ContributionUrl.objects.annotate(num_votes=Count('points')).all()
        b = ContributionAsk.objects.annotate(num_votes=Count('points')).all()
        result = sorted(chain(a, b), key=attrgetter('num_votes'), reverse=True)
        self.queryset = ContributionUrlAskSerializer(result).data
        return Response(self.queryset, status=status.HTTP_200_OK)



class SubmittedAPI(APIView):
    def get(self, request, username):
        try:
            api_key = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        usersended = UserProfile.objects.filter(apikey=api_key)

        if not api_key or not usersended:
            return Response({"error": "You provided no api key (X-API-KEY Header) or the one you provided is invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(username=username)
        if not user:
            return Response({"error": 'No User with that username'}, status=status.HTTP_404_NOT_FOUND)
        usernameProfile = UserProfile.objects.filter(user=user[0].id)
        if usernameProfile is usersended:
            return Response(status=status.HTTP_403_FORBIDDEN)

        contribution = Contribution.objects.filter(author=user[0]).order_by('-points')
        print(contribution)
        data = ContributionUrlAskSerializer(contribution).data
        return Response(data, status=status.HTTP_200_OK)