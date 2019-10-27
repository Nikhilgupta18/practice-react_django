from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model


User = get_user_model()


class Article(models.Model):
    author      = models.ForeignKey(User, on_delete=models.CASCADE)
    title       = models.CharField(max_length=200, null=True, blank=True, default=None)
    content     = RichTextUploadingField(null=True, blank=True, default=None)
    slug        = models.SlugField(max_length=200, null=True, blank=True, default=None)
    status      = models.CharField(max_length=100, default='in_review')
    thumbnail   = models.ImageField(upload_to="articles/", default=None, null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    no_of_views = models.IntegerField(default=0)
    social_links_allowed = models.BooleanField(default=True)

    def __str__(self):
        return str(self.title)

