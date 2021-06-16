from django.contrib import admin
from .models import Contribution, ContributionAsk, ContributionUrl, UserProfile, ContributionComment
# Register your models here.

admin.site.register(Contribution)
admin.site.register(ContributionAsk)
admin.site.register(ContributionUrl)
admin.site.register(UserProfile)
admin.site.register(ContributionComment)