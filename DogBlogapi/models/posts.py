from django.db import models
from .post_user import PostUser


class Post(models.Model):
    user = models.ForeignKey("PostUser", on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False)
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=2500)