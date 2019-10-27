from django.db import models
from django.contrib.auth import get_user_model
from account.storage import OverwriteStorage

User = get_user_model()


class Question(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, default=9999999)
    question        = models.TextField()
    path            = models.ImageField(upload_to="questions/", default=None, null=True, blank=True)
    details         = models.TextField()
    topic           = models.TextField()
    ques_link       = models.SlugField(max_length=500)
    timestamp       = models.DateTimeField(auto_now_add=True)
    no_of_ans       = models.IntegerField(default=0)
    views           = models.IntegerField(default=0)
    upvotes         = models.IntegerField(default=0)
    ques_liked_by   = models.ManyToManyField(User, default=0, related_name='ques_liked_by')
    followers       = models.ManyToManyField(User, default=None, related_name='followers')

    def __str__(self):
        return str(self.user) + ' [' + self.question + ']'


class Answer(models.Model):
    question    = models.ForeignKey(Question, on_delete=models.CASCADE, default=999999)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, default=9999999)
    details     = models.TextField(default=0)
    timestamp   = models.DateTimeField(auto_now_add=True)
    upvotes     = models.IntegerField(default=0)
    downvotes   = models.IntegerField(default=0)
    liked_by    = models.ManyToManyField(User, default=0, related_name='liked_by')
    disliked_by = models.ManyToManyField(User, default=0, related_name='disliked_by')

    def __str__(self):
        return str(self.user) + ' [' + self.details + ']'


class Views(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    q                   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='q')
    ip_address          = models.GenericIPAddressField(null=True, blank=True, default=None)
    is_anonymous        = models.BooleanField(default=False)
    latest_view_time    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + ' [' + str(self.q) + ']'
