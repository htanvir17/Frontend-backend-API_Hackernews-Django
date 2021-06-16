from django.urls import reverse
from django.db import models
from polymorphic.models import PolymorphicModel
from django.utils import timezone
from django.contrib.auth.models import User
import math
from django.db.models.signals import post_save
from django.dispatch import receiver
from social_core.backends import username

# from rest_framework_api_key.models import AbstractAPIKey
# from rest_framework_api_key.admin import APIKey

import binascii
import os
import base64


class Contribution(PolymorphicModel):
    id_contribution = models.AutoField(primary_key=True)
    title = models.TextField(max_length=80)
    creation_date = models.DateTimeField(auto_now_add=True)
    points = models.ManyToManyField(User,blank=True, related_name='points')
    author = models.ForeignKey(User, on_delete=models.CASCADE) #it means we have a relation: Contribution (*) ------ (1) User 
    comments = models.IntegerField(default=0)  # the number of comments related to it

    #this method represent 50 chars of title in Django Admin account to be descriptive and helpful representation of our database entry
    def __str__(self):
        return self.title[:50]

    #fe. when in form we click the button submit it will call this function to redirecto newest page
    def get_absolute_url(self):
        return reverse('newest') #function reverse(...) to have url format link

    def get_api_like_url(self):
        return reverse("votepost", kwargs={"id": self.id_contribution})

    def get_cname(self):
        return 'Contribution'
        
    def get_short_title(self):
        if len(self.title) > 50:
            return self.title[0:50] + "..."
        return self.title

    def whenpublished(self):
        now = timezone.now()

        diff = now - self.creation_date

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"

            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            if minutes == 1:
                return str(minutes) + " minute ago"

            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"

        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"

            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days / 30)

            if months == 1:
                return str(months) + " month ago"

            else:
                return str(months) + " months ago"

        if diff.days >= 365:
            years = math.floor(diff.days / 365)

            if years == 1:
                return str(years) + " year ago"

            else:
                return str(years) + " years ago"

    def getpoints(self):
        return (self.points.count() + 1) 

    def get_shortened_title(self):
        if len(self.title)>50:
            return self.title[:50] + '...'
        return self.title[:50]
    
    def get_uservoted(self):
        print("point is " )
        print(self.points)
        return self.points.values_list('username', flat=True)

    def get_uservoted(self):
        print("point is " )
        print(self.points)
        return self.points.values_list('username', flat=True)




class ContributionUrl(Contribution):
    url = models.URLField(unique=True)

    def get_cname(self):
        return 'ContributionUrl'

    def get_base_url(self):
        base = self.url.split("//")[-1].split("/")[0]
        return base

    def get_absolute_url(self):
        return reverse('newest')

    def get_id(self):
        return self.id_contribution




class ContributionAsk(Contribution):
    text = models.TextField(default="I am a text")

    def get_cname(self):
        return 'ContributionAsk'




class ContributionAskUrl(Contribution):
    url = models.URLField()
    text = models.TextField(default="I am a text")
    



class ContributionComment(Contribution):
    text = models.TextField(default="I am a comment")
    contribution_ref = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='+')
    parent = models.ForeignKey("self",on_delete=models.CASCADE, related_name='iam_reply', blank=True, null=True)
    
    def get_cname(self):
        return 'ContributionComment'

    def get_absolute_url(self):
        return reverse('ask')
    
    def __str__(self):
        return self.text[:50]

    def get_depth(self):
        original = Contribution.objects.get(id_contribution = self.contribution_ref.id_contribution)
        a = 1
        aux = Contribution.objects.get(id_contribution = self.parent.id_contribution)
        while aux.parent != None :
            a = a+1
            aux = Contribution.objects.get(id_contribution = aux.parent.id_contribution)
        return a*20
   
    def get_root(self):
        if self.parent:
            print("tengo padre")
            aux = Contribution.objects.get(id_contribution = self.parent.id_contribution)
        else:
            print("no tengo padre")
            aux = self
        while aux.get_cname == 'ContributionComment':
           aux = Contribution.objects.get(id_contribution = aux.parent.id_contribution)
        if len(aux.title) > 50:
            aux.title = aux.title[0:50] + "..."
        return aux
    
    @property
    def placeAlatitude(self):
        return self.contribution_ref.id_contribution




class Upvoted(models.Model):
    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500, blank=True)
    karma = models.IntegerField(default=1)

    #API key has to be unique
    apikey = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.user.username[:50]
    
    def whencreated(self):
        now = timezone.now()

        diff = now - self.user.date_joined

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"

            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            if minutes == 1:
                return str(minutes) + " minute ago"

            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"

        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"

            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days / 30)

            if months == 1:
                return str(months) + " month ago"

            else:
                return str(months) + " months ago"

        if diff.days >= 365:
            years = math.floor(diff.days / 365)

            if years == 1:
                return str(years) + " year ago"

            else:
                return str(years) + " years ago"    


def __apikey_generator(id,name):

    while len(name) < 20:
        name += (name + "-" + str(id))
    base_api = name[::-1]
    print(base_api)
    cifrado = base64.b64encode(base_api.encode("utf-8"))
    print(cifrado)
    cifrado = cifrado.decode("utf-8")
    cifrado_reverse = cifrado[::-1]
    print(cifrado_reverse)

    return cifrado_reverse


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        # Old way 
        # APIKey.objects.create_key(name=user.username)
        # up = UserProfile(user=user, about="", apikey=new_api_key[1])
        # up.save()
        #New way
        print(user.username)
        print(user.id)
        new_api_key = __apikey_generator(user.id,user.username)
        up = UserProfile(user=user, about="", apikey=new_api_key)
        up.save()

post_save.connect(create_profile, sender=User)  


    