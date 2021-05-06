from django import forms
from .models import NoticeComment

class NoticeCommentForm(forms.ModelForm):
    class Meta:
        model = NoticeComment
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Add Comment'})
        }