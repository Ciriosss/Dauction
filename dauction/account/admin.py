from django.contrib import admin
from .models import Account, Transaction,Recension

admin.site.register([Account,Transaction,Recension])
