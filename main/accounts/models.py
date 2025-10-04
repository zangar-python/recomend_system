from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Item(models.Model):
    author = models.ForeignKey(User,models.CASCADE,related_name="my_items")
    likes = models.ManyToManyField(User,related_name="likes")
    title = models.CharField(max_length=120)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name="ratings")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="ratings")
    added_at = models.DateField(auto_now_add=True)
    value = models.IntegerField()
    