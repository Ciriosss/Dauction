"""dauction URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from account import views as account_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login', auth_views.LoginView.as_view(template_name = 'account/login.html'), name = 'login'),
    path('profile/', account_views.profile, name = 'profile'),
    path('account/<int:pk>/', account_views.accountDetail, name = 'accountDetail'),
    path('setUpAccount/', account_views.setUpAccount, name = 'setUpAccount'),
    path('bio/', account_views.bio, name = 'bio'),
    path('home/', include('auction.urls')),
    path('', account_views.register, name='register'),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
