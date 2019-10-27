from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Article


class ArticleForm(forms.ModelForm):

    content = forms.CharField(widget=CKEditorUploadingWidget(attrs={'id': 'content'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Title', 'class': 'form-input form-control', 'maxlength': 200, 'id': 'title'}))

    class Meta:
        model = Article
        fields = ['title', 'content', 'thumbnail', 'social_links_allowed']

