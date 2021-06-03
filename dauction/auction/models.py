from django.db import models
from django.utils.timezone import now
from account.models import Account
from datetime import datetime
from .blockchain import signedAuction
import pytz
import jsonfield
import hashlib


class Item(models.Model):
    seller = models.ForeignKey(Account, on_delete=models.CASCADE)
    CATEGORIES = [
        ('TC','Tecnology'),
        ('CT','Clothes'),
        ('RE','Real estate'),
        ('AT','Antiques'),
        ('SP','Sport'),
        ('OT','Other' ),
    ]
    category = models.CharField(choices=CATEGORIES,max_length=15, default='Tecnology')
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=500)
    image = models.ImageField(null = True, blank = True, upload_to="images/")

class Auction(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    starterPrice = models.FloatField()
    published = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(default= now)
    selleraddress = models.CharField(max_length=50, default=" ", blank=False)
    jsonResult = jsonfield.JSONField(max_length=500, default = {})
    winner = models.ForeignKey(Account, on_delete=models.CASCADE, default="", blank=True)
    jsonHash = models.CharField(max_length=100, default="", blank = True)
    txId = models.CharField(max_length=100, default="", blank = True)

    def is_expired(self):
        now = datetime.now()
        now = pytz.utc.localize(now)
        if now > self.expiration:
            return True
        return False

    def writeOnChain(self):
        self.jsonHash = hashlib.sha256(self.jsonResult.encode('utf-8')).hexdigest()
        self.txId = signedAuction(self.hash)
        self.save()

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, default="")
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
