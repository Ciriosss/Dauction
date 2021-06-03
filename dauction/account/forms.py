from django import forms
from .models import Account
from auction.models import Comment
from auction.models import Bid
from django.contrib.auth.forms import UserCreationForm


class AccountRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', ]


class newBid(forms.ModelForm):
    amount = forms.FloatField()

    class Meta:
        model = Bid
        fields = ['amount']

class SetUpAccount(forms.ModelForm):
    privateKey = forms.CharField(max_length=64)

    class Meta :
        model = Account
        fields = ['privateKey']

class newComment(forms.ModelForm):
    comment = forms.Textarea()

    class Meta :
        model = Comment
        fields = ['comment']

class newBio(forms.ModelForm):
    bio = forms.Textarea()

    class Meta :
        model = Account
        fields = ['bio']


