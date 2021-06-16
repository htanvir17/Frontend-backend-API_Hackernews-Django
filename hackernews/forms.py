from django import forms

class SubmitEditForm(forms.Form):
    #Used by both Submit and Edit
    title = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '50'}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '50'}))
    text = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': '4', 'cols': '49'}))
    #Used just by Submit
    author_id = forms.CharField(required=False)
    #Used just by Edit
    id = forms.CharField(required=False)
    goto = forms.CharField(required=False)



class CommentForm(forms.Form):
    parent = forms.CharField(required=True)
    parentcomment = forms.CharField(required=False)
    goto =  forms.CharField(required=True)
    text = forms.CharField(widget=forms.Textarea)
    author_id = forms.CharField(required=True)



class ConfirmDeleteForm(forms.Form):
    id = forms.CharField(required=True)
    goto = forms.CharField(required=True)
    # The values of answer can only be Yes or No
    answer =  forms.CharField(required=True,max_length=3)
    cname = forms.CharField(required=False)



class EditCommentForm(forms.Form):
    id = forms.CharField(required=False)
    text = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': '4', 'cols': '49'}))
