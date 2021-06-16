from rest_framework import serializers

from ..models import Contribution, ContributionUrl, ContributionAsk, ContributionComment, UserProfile, ContributionAskUrl

# the asks contribution recived will transform in this style, and then will 
class ContributionAskSerializer():
    data = None # this is a variable, so when we call from api_view, we can acces this variable
    def __init__(self,contributions,many=False):
        if not many:
            self.data = {
                'id_contribution': contributions.id_contribution,
                'title':contributions.title,
                'creation_date':contributions.creation_date,
                'text':contributions.text,
                'author':contributions.author.username,
                'points': contributions.getpoints(),
                'uservotes': contributions.get_uservoted(),
                'comments': contributions.comments
            }
        else:
            self.data = []
            for contrib in contributions:
                serializedAsk  = {
                    'id_contribution': contrib.id_contribution,
                    'title':contrib.title,
                    'creation_date':contrib.creation_date,
                    'text':contrib.text,
                    'author':contrib.author.username,
                    'points': contrib.getpoints(),
                    'uservotes': contrib.get_uservoted(),
                    'comments': contrib.comments
                }
                self.data.append(serializedAsk)



class ContributionUrlSerializer():
    data = None
    def __init__(self,contributions,many=False):
        if not many:
            self.data = {
                'id_contribution': contributions.id_contribution,
                'title':contributions.title,
                'creation_date':contributions.creation_date,
                'url': contributions.url,
                'author':contributions.author.username,
                'points': contributions.getpoints(),
                'uservotes': contributions.get_uservoted(),
                'comments': contributions.comments
            }
        else:
            self.data = []
            for contrib in contributions:
                serializedAsk  = {
                    'id_contribution': contrib.id_contribution,
                    'title':contrib.title,
                    'creation_date':contrib.creation_date,
                    'url':contrib.url,
                    'author':contrib.author.username,
                    'points': contrib.getpoints(),
                    'uservotes': contrib.get_uservoted(),
                    'comments': contrib.comments
                }
                self.data.append(serializedAsk)
        


class ContributionCommentSerializer():
    data = None
    def __init__(self,contributions,many=False):
        if not many:
            self.data = {
                'id_contribution': contributions.id_contribution,
                'text':contributions.text,
                'creation_date':contributions.creation_date,
                'author':contributions.author.username,
                'contribution_ref':contributions.contribution_ref.id_contribution,
                'points': contributions.getpoints(),
                'uservotes': contributions.get_uservoted(),
            }
        else:
            self.data = []
            for contrib in contributions:
                serializedAsk  = {
                    'id_contribution': contrib.id_contribution,
                    'text':contrib.text,
                    'creation_date':contrib.creation_date,
                    'author':contrib.author.username,
                    'contribution_ref':contrib.contribution_ref.id_contribution,
                    'points': contrib.getpoints(),
                    'uservotes': contrib.get_uservoted(),
                }
                self.data.append(serializedAsk)



class ContributionReplySerializer():
    data = None
    def __init__(self,contributions,many=False):
        if not many:
            self.data = {
                'id_contribution': contributions.id_contribution,
                'text':contributions.text,
                'creation_date':contributions.creation_date,
                'author':contributions.author.username,
                'contribution_ref':contributions.contribution_ref.id_contribution,
                'parent': contributions.parent.id_contribution,
                'points': contributions.getpoints(),
                'uservotes': contributions.get_uservoted(),
            }
        else:
            self.data = []
            for contrib in contributions:
                serializedAsk  = {
                    'id_contribution': contrib.id_contribution,
                    'text':contrib.text,
                    'creation_date':contrib.creation_date,
                    'author':contrib.author.username,
                    'contribution_ref':contrib.contribution_ref.id_contribution,
                    'parent': contrib.parent.id_contribution,
                    'points': contrib.getpoints(),
                    'uservotes': contrib.get_uservoted(),
                }
                self.data.append(serializedAsk)
    


class ProfileSerializer():
    def data (self,profiles):
        if len(profiles) == 1:
            profile_serialized={'id': profiles[0].user.id, 'username': profiles[0].user.username,'created': profiles[0].user.date_joined, 'karma': profiles[0].karma,'about': profiles[0].about}
            return profile_serialized
        else: # diferent than 1
            profiles_serialized = []
            for item in profiles:
                extended_profile= {
                                'id': item.user.id,
                                'username': item.user.username,
                                'created': item.user.date_joined,
                                'karma': item.karma,
                                'about': item.about}
                profiles_serialized.append(extended_profile)
            return profiles_serialized




class CommentsThreadsSerializer():
    def data(self,comment):
        Thread  = {
            'id_contribution': comment.id_contribution,
            'text':comment.text,
            'creation_date':comment.creation_date,
            'author':comment.author.username,
            'contribution_ref':comment.contribution_ref.id_contribution,
            'contribution_ref_title':comment.contribution_ref.get_short_title()
        }
        if comment.parent is not None: 
            Thread['parent'] = comment.parent.id_contribution
        
        Thread['points'] = comment.getpoints()
        Thread['uservotes'] = comment.get_uservoted()
        repliesSerializedList = []
        replies_list = ContributionComment.objects.filter(parent = comment.id_contribution)
        for reply in replies_list:
            repliesSerializedList.append(self.data(reply))
        Thread['replies'] = repliesSerializedList
        return Thread



class ContributionUrlAskSerializer():
    data = None
    def __init__(self, contributions):
        self.data = []
        for contrib in contributions: 
            typeClass = contrib.get_cname()
            if typeClass == 'ContributionAsk':
                serialized = {
                    'id_contribution': contrib.id_contribution,
                    'title': contrib.title,
                    'creation_date': contrib.creation_date,
                    'text': contrib.text,
                    'author': contrib.author.username,
                    'points': contrib.getpoints(),
                    'uservotes': contrib.get_uservoted(),
                    'comments':contrib.comments,
                    'type': "ASK"
                }
                self.data.append(serialized)
            elif typeClass == 'ContributionUrl':
                serialized = {
                    'id_contribution': contrib.id_contribution,
                    'title': contrib.title,
                    'creation_date': contrib.creation_date,
                    'url': contrib.url,
                    'author': contrib.author.username,
                    'points': contrib.getpoints(),
                    'uservotes': contrib.get_uservoted(),
                    'comments': contrib.comments,
                    'type': "URL"
                }
                self.data.append(serialized)