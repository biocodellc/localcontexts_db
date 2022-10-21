from django import forms
from .models import *
from django.forms import modelformset_factory, inlineformset_factory

AddLabelTranslationFormSet = modelformset_factory(
    LabelTranslation,
    fields=('translated_name', 'language', 'translated_text', ),
    extra=1,
    widgets = {
        'translated_name': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Customized label name'}),
        'language': forms.TextInput(attrs={'id': 'languageListInput', 'class': 'w-100', 'placeholder': 'Language', 'autocomplete': 'off'}),
        'translated_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'style': 'height: 150px; padding: 10px;'}),
    }
)

UpdateBCLabelTranslationFormSet = inlineformset_factory(
    BCLabel, LabelTranslation, 
    fields=('translated_name', 'language', 'translated_text',),
    extra=0,
    widgets = {
        'translated_name': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Customized label name'}),
        'language': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Language'}),
        'translated_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'style': 'height: 150px; padding: 10px;'}),
    }
)

UpdateTKLabelTranslationFormSet = inlineformset_factory(
    TKLabel, LabelTranslation, 
    fields=('translated_name', 'language', 'translated_text',),
    extra=0,
    widgets = {
        'translated_name': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Customized label name'}),
        'language': forms.TextInput(attrs={'class': 'w-100', 'placeholder': 'Language'}),
        'translated_text': forms.Textarea(attrs={'class': 'w-100 margin-top-1 margin-bottom-2', 'style': 'height: 150px; padding: 10px;'}),
    }
)

class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'w-100', 'style': 'height: 111px; padding: 10px;', 'placeholder': 'Add comment'})
        }

class LabelNoteForm(forms.ModelForm):
    class Meta:
        model = LabelNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'class': 'w-100 margin-bottom-2', 'style': 'height: 150px; padding: 10px;', 'placeholder': 'Add Note About This Label'}),
        }

class OpenToCollaborateNoticeURLForm(forms.ModelForm):
    class Meta:
        model = OpenToCollaborateNoticeURL
        fields = ['name', 'url']
        widgets = { 
            'name': forms.TextInput(attrs={'class': 'w-100 margin-bottom-8'}), 
            'url': forms.TextInput(attrs={'class': 'w-100'}), 
        }

class LabelVersionForm(forms.ModelForm):
    class Meta:
        model = LabelVersion
        fields = ['version_text']
        widgets = { 
            'version_text': forms.Textarea(attrs={'class': 'w-100'}), 
        }