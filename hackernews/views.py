from itertools import chain
from operator import attrgetter

from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse,resolve
from django.views.generic import TemplateView, ListView , UpdateView
from django.db import IntegrityError
from django.views import View
from django.views.generic.edit import CreateView
from .forms import CommentForm, SubmitEditForm, ConfirmDeleteForm, EditCommentForm
from django.http import HttpResponse, HttpResponseRedirect, request
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

# Create your views here.
from .models import Contribution, ContributionUrl, ContributionAsk, ContributionComment, UserProfile
import base64

# The order of the clases in this code is the same as the header order of the hackernews page

#we are in HomePage = "/", return object_list = contribution list to render
#this class inherits all funcionalities of ListView
class HomePageView(ListView):
    context_object_name = 'contribution_list' #we change default name of "object list", be careful in home.html to take data
    template_name = 'home.html' #we will send data in this template to show 

    #this method execute when urls.py call; returns all contributions ordered by vote points; this function is the same to have a variable like (queryset = ..)
    def get_queryset(self):
        a = ContributionUrl.objects.annotate(num_votes=Count('points')).all()
        b = ContributionAsk.objects.annotate(num_votes=Count('points')).all()
        result = sorted(chain(a, b), key=attrgetter('num_votes'), reverse=True)
        return result

    #this method execute when urls.py call; this method is to have "context object"
    def get_context_data(self, **kwargs):
        name = "kennyangelsytem15"
        id = 1
        print(len(name))
        while len(name) < 20:
            name += (name + "-" + str(id))
        base_api = name[::-1]
        print(base_api)
        cifrado = base64.b64encode(base_api.encode("utf-8"))
        print(cifrado)
        cifrado = cifrado.decode("utf-8")
        cifrado_reverse = cifrado[::-1]
        print(cifrado_reverse)
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)

            own = Contribution.objects.filter(author__in=[self.request.user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
        return context



# send all contributions ordered by date to /newest (don't forgot that this is a class, inside we have functions that do this task)
class NewestPageView(ListView):
    template_name = 'newest.html'
    context_object_name = 'contribution_list'
    
    def get_queryset(self):
        a = ContributionUrl.objects.all()
        b = ContributionAsk.objects.all()
        result = sorted(chain(a, b), key=attrgetter('creation_date'), reverse=True)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #define our context in base
        context["current_page"] = "newest" #send this key:value to base.html; rememeber that we are in /newest but inside we have base.html
        
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)

            own = Contribution.objects.filter(author__in=[self.request.user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
            
        return context



# get ask contributions to render in /ask page
class AskPageView(ListView): 
    queryset = ContributionAsk.objects.all().order_by('-creation_date')
    context_object_name = 'contribution_list'
    template_name = 'ask.html'

    def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          context["current_page"] = "ask"

          if self.request.user.is_authenticated:
              voted = Contribution.objects.filter(points__in=[self.request.user])
              voted = voted.values_list('id_contribution', flat=True)

              own = Contribution.objects.filter(author__in=[self.request.user])
              own = own.values_list('id_contribution', flat=True)
              context["own"] = own
              context["voted"] = voted

          return context



# show form and also take form values to save in DB
class SubmitPageView(View):
    form_class = SubmitEditForm #we specify which form we are going to use, this form is defined in forms.py instead of html
    initial = {'key': 'value'}
    template_name = 'submit.html'

    # when user what to GET form
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial) #in this variable set the form
        form.title = "Title"
        return render(request, self.template_name, {'form': form}) #send to render

    # when user want to POST a contribution and we have to check that doesn't violate any restrictions
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        title = form['title'].value()
        url = form['url'].value()
        text = form['text'].value()
        author_id = form['author_id'].value()
        author_sended = User.objects.get(id=author_id) #object

        if author_sended == None:
            form.add_error('User does not exist', 'Please try again.')
            return HttpResponse(render(request, self.template_name, {'form': form}))

        # RT: Posting too fast
        contributionAsk = ContributionAsk.objects.filter(author=author_id)
        contributionUrl = ContributionUrl.objects.filter(author=author_id)
        datetimeNow = datetime.now() - timedelta(hours=1)
        sub_in_last_hour = 0
        for i in contributionAsk:
            if i.creation_date > datetimeNow:
                sub_in_last_hour = sub_in_last_hour + 1
        for i in contributionUrl:
            if i.creation_date > datetimeNow:
                sub_in_last_hour = sub_in_last_hour + 1
        if sub_in_last_hour > 5:
            return HttpResponseRedirect(reverse('too_fast'))

        # RT: title; in submit.html we just show this error related to title
        if title == "":
            form.add_error('title', 'Please try again.') 
            return HttpResponse(render(request, self.template_name, {'form': form}))
        if len(title) > 80:
            form.add_error('title', "Please limit title to 80 characters. This had  " + str(len(title)) + ".")
            return HttpResponse(render(request, self.template_name, {'form': form}))

        # RT: url
        if url != "":
            if text == "":
                try:
                    urlC = ContributionUrl(title=title, url=url, creation_date=datetime.now(), author=author_sended)
                    urlC.save()
                except IntegrityError as e: #this except will be thrown if already exista the url because in model we defined to be unique; in that case we have to redirect in the url
                    if 'UNIQUE constraint failed' in e.args[0]:
                        url_existent = ContributionUrl.objects.filter(url=url)
                        print(url_existent)
                        # form.add_error('title', 'URL already exist. Unique')
                        # return HttpResponse(render(request, self.template_name, {'form': form}))
                        return HttpResponseRedirect('/item?id=%s' % (url_existent[0].id_contribution))
                        # return redirect('item/id?' + str(url_existent.get_id()))
            else:
                form.add_error('title',
                               "Submissions can't have both urls and text, so you need to pick one. If you keep the url, you can always post your text as a comment in the thread.")
                return HttpResponse(render(request, self.template_name, {'form': form}))
        else:
            ask = ContributionAsk(title=title, text=text, creation_date=datetime.now(), author=author_sended)
            ask.save()
        return HttpResponseRedirect(reverse('newest'))




class TooFastView(TemplateView):
    template_name = "too_fast.html"



#when we select a contribution from /newest or /, it will send here to contact with html to detail the contribution
class ItemPageView(ListView):
    template_name = 'item.html'
    context_object_name = 'contribution' #we will send the particular contribution selected
    
    # IMPORTANT: notice that it is an override of a predefined method, what it does is we get the parameters of query expresed inside a URL; i.e. https ....../item?id=id_contribution
    def get_queryset(self):
        if self.request.method == 'GET':
            id_item = self.request.GET.get('id') #get contribution id and we will to evalute whether is ask or url
            contrib = None
            if ContributionAsk.objects.filter(id_contribution=id_item).exists():
                contrib =  ContributionAsk.objects.filter(id_contribution=id_item)[0]
            elif ContributionUrl.objects.filter(id_contribution=id_item).exists():
                contrib =  ContributionUrl.objects.filter(id_contribution=id_item)[0]
            elif ContributionComment.objects.filter(id_contribution=id_item).exists():
                contrib = ContributionComment.objects.filter(id_contribution=id_item)[0]
            else:
                return None
            return contrib
        else:
            print('I am not a GET request')
        return None

    def get_context_data(self, **kwargs):
        context = super(ItemPageView, self).get_context_data(**kwargs)
        
        # if the contribution have comments, we will send in item.html
        if self.object_list.get_cname() != 'ContributionComment':
            context['comentaris'] = ContributionComment.objects.filter(contribution_ref=self.object_list, parent__isnull=True) # we will get all descendent contribution from 'contribution'
            aux = list(context['comentaris'])
        else:
            id_item = self.request.GET.get('id')
            context['comentaris'] = ContributionComment.objects.filter(id_contribution=id_item)
            aux = list(context['comentaris'])
            
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)

            own = Contribution.objects.filter(author__in=[self.request.user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
        return context



#this class just check and store the comment written by user, it will be called from Item page
class CommentPageView(TemplateView):
    # This TemplateView doesn't require an explicit template_name because we just need post method
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST) # we take the params of form by request.POST (remember that we had taken some value in hidden) and create this form
        # It's necessary to do a is_valid method before to call cleaned_data (like a dictonary, will  only contain a key for fields defined in the Form)
        if form.is_valid():
            # create a contributionComment
            obj_parent = Contribution.objects.get(id_contribution=form.cleaned_data['parent'])
            author_new_contribution = User.objects.get(id=form.cleaned_data['author_id'])
            
            if form.cleaned_data['parentcomment'] != "null" : #if this coment has parent, we will have to indicate in DB
                parentcomment = Contribution.objects.get(id_contribution=form.cleaned_data['parentcomment'])
                comment = ContributionComment(text=form.cleaned_data['text'], contribution_ref=obj_parent,
                                         parent=parentcomment, author=author_new_contribution)
            else:
                comment = ContributionComment(text=form.cleaned_data['text'], contribution_ref=obj_parent, author=author_new_contribution)
            print(ContributionComment.objects.all().count())

            # This method save the object in the database. It's a method clasified as a procedure that means it returns nothing (None in Python)
            print(comment.save() == None)
            # This line updates the comments atribute that the contribution parent has.
            obj_parent.comments = obj_parent.comments + 1 # we have to increment comments number 
            obj_parent.save()
            print(ContributionComment.objects.all().count())

        return HttpResponseRedirect(form.cleaned_data['goto']) #the url that we save in item.html (in a form)



#update a contribution (ask or url), /edit?id=x; we will send a contribution to edit.html (this work will do get_my_queryset)
class EditPageView(ListView):
    form_class = SubmitEditForm #use the same form of submit but with two params extra (forms.py)
    template_name = 'edit.html'

    #get the contribution
    def get_my_queryset(self):
        try:
            if self.request.method == 'GET':
                id_item = self.request.GET.get('id')
            else:
                id_item = self.request.POST.get('id')

            if ContributionAsk.objects.filter(id_contribution=id_item).exists():
                return ContributionAsk.objects.filter(id_contribution=id_item)
            elif ContributionUrl.objects.filter(id_contribution=id_item).exists():
                return ContributionUrl.objects.filter(id_contribution=id_item)
            elif ContributionComment.objects.filter(id_contribution=id_item).exists():
                return ContributionComment.objects.filter(id_contribution=id_item)
            else:
                return None
        except:
            return None

    #when edit.html wants to show the form, call this method (when we go /edit?id=x first call get_my_queryset() and then get())
    def get(self, request, *args, **kwargs):
        object_list = self.get_my_queryset() #get contribution
        id_item = self.request.GET.get('id')
        if ContributionAsk.objects.filter(id_contribution=id_item).exists():
            contrib = ContributionAsk.objects.filter(id_contribution=id_item)
            initial_value = {'title': contrib[0].title, 'text': contrib[0].text}
        elif ContributionUrl.objects.filter(id_contribution=id_item).exists():
            contrib = ContributionUrl.objects.filter(id_contribution=id_item)
            initial_value = {'title': contrib[0].title}
        elif ContributionComment.objects.filter(id_contribution=id_item).exists():
            comment = ContributionComment.objects.filter(id_contribution=id_item)
            self.form_class = EditCommentForm
            self.template_name = 'editComment.html'
            return render(request,self.template_name, {'form': self.form_class, 'object_list': object_list})
        else:
            return render(request,self.template_name, {'object_list': object_list})

        form = self.form_class(initial=initial_value)
        # If you want to save the content of a variable you have to send it in the render; for example of object_list
        return render(request, self.template_name, {'form': form, 'object_list': object_list})

    #user want to update the contribution, so we have to check RT before save in DB
    def post(self, request, *args, **kwargs):
        aux_comment_id = self.request.POST.get('id')
        #user want to edit its comments
        if ContributionComment.objects.filter(id_contribution=aux_comment_id).exists():
            form = EditCommentForm(request.POST)
            self.form_class = EditCommentForm
            object_list = self.get_my_queryset()
            print(form.data)
            text_aux = form.data['text']
            if not text_aux == "":
                ContributionComment.objects.filter(id_contribution=aux_comment_id).update(text = text_aux)
            return HttpResponseRedirect('/edit?id=%s' % ( aux_comment_id ))
        
        form = self.form_class(request.POST)
        # It's necessary to do a is_valid method before we call cleaned_data
        if form.is_valid():
            # in this case, the contribution will be ask or url
            id_item = form.cleaned_data['id']
            new_title = form.cleaned_data['title']
            new_text = form.cleaned_data['text']
            goto = form.cleaned_data['goto']
            object_list = self.get_my_queryset()
            
            if new_title == "":
                form.add_error('title', 'Title can not be empty. Please try again.')
                # return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
                # request.resolver_match.url_name
                # In order to refresh the page we must sent again the object_list and the form
                return render(request, self.template_name, {'form': form, 'object_list': object_list})
            if len(new_title) > 80:
                form.add_error('title', 'Title can not be longer than 80 characters. Please try again.')
                return render(request, self.template_name, {'form': form, 'object_list': object_list})

            if object_list[0].get_cname() == 'ContributionAsk':
                if new_text == "":
                    form.add_error('title', 'Text can not be empty. Please try again.')
                    return render(request, self.template_name, {'form': form, 'object_list': object_list})
                else:
                    ContributionAsk.objects.filter(id_contribution=id_item).update(title=new_title, text=new_text)
                    # Be careful with the result of the object_list, if this doesn't show what it has to show then uncommented the following line.
                    # object_list = self.get_my_queryset()
                    return render(request, self.template_name, {'form': form, 'object_list': object_list})
            # ContributionUrl
            ContributionUrl.objects.filter(id_contribution=id_item).update(title=new_title)
            # Be careful with the result of the object_list.If this doesn't show what it has to show then uncommented the following line.
            # object_list = self.get_my_queryset()
            return render(request, self.template_name, {'form': form, 'object_list': object_list})
        return HttpResponseRedirect(reverse('newest'))



#when user want to delete a contribution like ask, url or comment
class DeletePageView(ListView):
    template_name = 'delete.html'

    #we will send in detele.html the contribution and the previous url
    def get_queryset(self):
        if self.request.method == 'GET':
            caller_URL = self.request.META.get('HTTP_REFERER') #we take the previous url
            try:
                id_item = self.request.GET.get('id')
                # We sent two objects of different type to be read in the template
                queryset = [Contribution.objects.filter(id_contribution=id_item)[0], caller_URL] #we will send an vector that contain contribution and previous url
                return queryset
            except:
                return None
        return None

    #when user answer the delete message warning, and we have to analyze
    def post(self, request, *args, **kwargs):
        form = ConfirmDeleteForm(request.POST) #we will create this form passing the form values gotten in delete.html form
        # This function is valid only if all the conditions specified for the form (in this case ConfirmDeleteForm) are fit
        if form.is_valid():
            if form.cleaned_data['answer'] == "Yes":
                Contribution.objects.filter(id_contribution=form.cleaned_data['id']).delete()
                if form.cleaned_data['cname'] == 'ContributionComment':
                    return HttpResponseRedirect(form.cleaned_data['goto'])
                return HttpResponseRedirect(reverse('home'))
            else:
                # When the previous page is unknown goto  has a is /None at the end
                if form.cleaned_data['goto'].find("/None"):
                    return HttpResponseRedirect(reverse('home'))
                else:
                    return HttpResponseRedirect(form.cleaned_data['goto'])
        else:
            return None


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)

            own = Contribution.objects.filter(author__in=[self.request.user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
        return context



#update profile; When we use UpdateView we can access to self.object, which is the object being updated
class ProfilePageView(UpdateView):
    model = UserProfile #check this model
    template_name = 'userProfile.html'
    fields = ['about'] #for using UpdateView we can mention field that we have declared in model, and can send it in template

    #send user object; this function is always called when we acces userProfile.html, whether it is GET or POST
    def get_object(self):
        if self.request.method == 'GET' or self.request.method == 'POST':
            id_profile = self.request.GET.get('id')
            if User.objects.filter(username=id_profile).exists():
                usuariaux = User.objects.get(username=id_profile)
                return UserProfile.objects.get(user=usuariaux)
            else:
                None
        else:
            print('I am not a GET or POST request')
        return None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)

            own = Contribution.objects.filter(author__in=[self.request.user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
        return context

    #i think we don't use
    def form_valid(self, form):
        perfil_aux = UserProfile(user=self.request.user)
        profile = form.save(commit=False)
        profile.karma = perfil_aux.karma
        profile.user = self.request.user
        profile.save()

        return HttpResponseRedirect('/user?id=%s' % (profile.user))




class FomatDocPageView(TemplateView):
    template_name = 'formatdoc.html'



#when an user vote or upvote a contribution like ask, url or comment, we have to update 
class PostLikeAPIToggle(APIView):
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



#when an user want to see upvoted contribution list
class UpvotedContributions(ListView):  
    context_object_name = 'contribution_list'
    template_name = 'upvotedcontributions.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Contribution.objects.filter(points=self.request.user).order_by('-points')
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"]= "upvoted"
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)

            own = Contribution.objects.filter(author__in=[self.request.user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
        return context




#when an user want to see only your upvoted comment list
class UpvotedComments(ListView):
    context_object_name = 'contribution_list'
    template_name = 'upvotedcomments.html'

    #get all user comment
    def get_queryset(self):
        return ContributionComment.objects.filter(points=self.request.user).order_by('-creation_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"]= "upvoted"
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)

            own = Contribution.objects.filter(author__in=[self.request.user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
        return context



#when an user want to see the submissions that does
class SubmissionsPageView(ListView):
    context_object_name = 'contribution_list'
    template_name = 'submitted.html'

    #return all user contribution
    def get_queryset(self, *args, **kwargs):
        auth = self.request.GET.get('id', None)
        user = User.objects.get(username=auth)
        contUrl = ContributionUrl.objects.filter(author=user)
        contAsk = ContributionAsk.objects.filter(author=user)
        result = sorted(chain(contUrl, contAsk), key=attrgetter('creation_date'), reverse=True)
        return result
      
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"] = "submissions"
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[self.request.user])
            voted = voted.values_list('id_contribution', flat=True)
            context["voted"] = voted
        return context



#when an user want to see all their comment comments
class ThreadsPageView(TemplateView):
    # This TemplateView doesn't require an explicit template_name
    template_name = 'threads.html'

    #we don't use queryset but instead of this we send all comment in context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_page"] = "threads"   
        selected_user = User.objects.get(username = self.request.GET.get('id'))
        if self.request.user.is_authenticated:
            voted = Contribution.objects.filter(points__in=[selected_user])
            voted = voted.values_list('id_contribution', flat=True)
            own = Contribution.objects.filter(author__in=[selected_user])
            own = own.values_list('id_contribution', flat=True)
            context["own"] = own
            context["voted"] = voted
           
        context["comments"] = ContributionComment.objects.filter(author__in=[selected_user])
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        
        if form.is_valid():
            obj_parent = Contribution.objects.get(id_contribution=form.cleaned_data['parent'])
            author_new_contribution = User.objects.get(id=form.cleaned_data['author_id'])
            comment = ContributionComment(text=form.cleaned_data['text'], contribution_ref=obj_parent,
                                          author=author_new_contribution)
            print(ContributionComment.objects.all().count())

            print(comment.save() == None) #save it
            # This line updates the comments atribute that the contribution parent has.
            obj_parent.comments = ContributionComment.objects.all().count()
            obj_parent.save()
            print(ContributionComment.objects.all().count())

        return HttpResponseRedirect(form.cleaned_data['goto'])



#when an user want to reply a comment
class ReplyView(ListView):
    form_class = CommentForm
    template_name = 'replyComment.html'
    context_object_name = 'contribution_list'

    def get_queryset(self):
        if self.request.method == 'GET':
            id_contrib = self.request.GET.get('id')
            if Contribution.objects.filter(id_contribution = id_contrib).exists():
                return Contribution.objects.filter(id_contribution = id_contrib)
        return None
    
    def post(self, request):
        form = self.form_class(request.POST)
        print(form.data)
        if form.is_valid:
            goto = form.data['goto']
            text = form.data['text']
            if text == "":
                return HttpResponseRedirect('/reply?id=%s' % form.data['parentcomment'])
            parent = Contribution.objects.get(id_contribution = form.data['parent'])
            parentComment = ContributionComment.objects.get(id_contribution = form.data['parentcomment'])

            print(parent.comments)
            parent.comments = parent.comments + 1
            parent.save()
            reply = ContributionComment(author = self.request.user,contribution_ref=parent,
            text = text, parent =parentComment )
            st = reply.save()
            return HttpResponseRedirect(goto)
        
        return HttpResponseRedirect('/reply?id=%s' % form.data['parentcomment'])


    
