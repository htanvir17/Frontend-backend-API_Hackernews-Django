from django import template
from ..models import UserProfile
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    updated.update(kwargs)
    return updated.urlencode()

@register.simple_tag(takes_context=True)
def get_karma(context,format_string):
    print('inside_get karma')
    user = context['user']
    karma =  UserProfile.objects.filter(id=user.id)[0].karma
    return karma
        
@register.simple_tag(takes_context=True)
def get_parameter_id(context,format_string):
    username = context['request'].GET.get("id")
    print(username)
    return username

@register.simple_tag(takes_context=True)
def get_parameter_id(context,format_string):
    username = context['request'].GET.get("id")
    print(username)
    return username
