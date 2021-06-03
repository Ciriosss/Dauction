from django.shortcuts import render, redirect
from django.contrib import messages
from . models import Account, Recension
from .forms import AccountRegisterForm, SetUpAccount
from auction.blockchain import newAccount
from django.contrib.auth.decorators import login_required

def register( request):

    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,'Congratulations {}! your account has been created successfully, now you are able to log-in'.format(username))
            return redirect('login')
    else:
        form = AccountRegisterForm()
    return render(request, 'account/register.html', {'form': form})

@login_required(login_url='login')
def profile(request):
    account = request.user
    return render(request, 'account/profile.html', {'account': account})

def accountDetail(request, pk):
    account = Account.objects.get(pk = pk)
    recensions = Recension.objects.filter(to = account)
    if request.method == 'POST':
        recension = request.POST.get('recension')
        rating = request.POST.get('rating')

        Recension.objects.create(author = request.user, recension = recension, rating = rating, to = account)
    return render(request, 'account/accountDetail.html', {'account': account, 'recensions' : recensions})

def setUpAccount(request):

    if request.method == 'POST':
        form = SetUpAccount(request.POST)

        if form.is_valid():
            account = request.user
            privateKey = form.cleaned_data.get('privateKey')

            try:
                newAccount(account,privateKey)
            except:
                messages.warning(request, 'Not valid Private Key, try again')
                return redirect('profile')

            return redirect('profile')
    else:
        form = SetUpAccount()
    return render(request, 'account/setUpAccount.html', {"form" : form})

