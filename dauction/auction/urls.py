from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = "home"),
    path('items/', views.items, name="items"),
    path('fiterByCategory/<str:category>/', views.fiterByCategory, name = "fiterByCategory"),
    path('auction/<int:pk>', views.auction, name="auction"),
    path('newAuction/', views.newAuction, name="newAuction"),
    path('transactions/', views.transactions, name="transactions"),
    path('transaction/<str:tx>/', views.transactionDetail, name = "transactionDetail"),
    path('auctionsFinished', views.auctionsFinished, name = "auctionsFinished")
]
