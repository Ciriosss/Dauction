from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    address = models.CharField(max_length=50, default="")
    encrypt = models.TextField(max_length=5000, default="")


class Transaction(models.Model):
    addressFrom = models.TextField(max_length=50)
    addressTo = models.TextField(max_length=50)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    tx = models.TextField(max_length=100)

