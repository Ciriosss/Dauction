from django.contrib import admin
from .models import Item, Auction, Bid

admin.site.register([Item, Auction, Bid])