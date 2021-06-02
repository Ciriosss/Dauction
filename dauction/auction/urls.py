from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = "home"),
    path('items/', views.items, name="items"),
    path('auction/<int:pk>', views.auction, name="auction"),
    path('newAuction', views.newAuction, name="newAuction"),
]
