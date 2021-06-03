from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField

class Account(AbstractUser):
    address = models.CharField(max_length=50, default="")
    encrypt = models.TextField(max_length=5000, default="")
    bio = RichTextField(blank = True, null = True)

class Transaction(models.Model):
    addressFrom = models.CharField(max_length=50)
    addressTo = models.CharField(max_length=50)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    tx = models.CharField(max_length=100)

class Recension(models.Model):
    author = models.ForeignKey(Account,on_delete=models.CASCADE, related_name='author')
    recension = models.TextField(max_length=500)
    rating = models.IntegerField()
    to = models.ForeignKey(Account,on_delete=models.CASCADE, related_name='to')