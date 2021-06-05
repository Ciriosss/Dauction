from django.shortcuts import render, redirect
from django.contrib import messages
from . models import Account, Recension
from .forms import AccountRegisterForm, SetUpAccount, newBio
from auction.blockchain import newAccount
from django.contrib.auth.decorators import login_required
from auction.blockchain import getBalance

#register view
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

#profile page
@login_required(login_url='login')
def profile(request):
    account = request.user
    balance = 0
    if account.address:
        balance = getBalance(account.address)
    return render(request, 'account/profile.html', {'account': account, 'balance': balance})

#personal page of other user, here people can leave a recension
def accountDetail(request, pk):
    account = Account.objects.get(pk = pk)
    recensions = Recension.objects.filter(to = account).order_by('-datetime')
    if request.method == 'POST':
        recension = request.POST.get('recension')
        rating = request.POST.get('rating')

        Recension.objects.create(author = request.user, recension = recension, rating = rating, to = account)
    return render(request, 'account/accountDetail.html', {'account': account, 'recensions' : recensions})

#view for set up an ethereum account(metamask alternative))
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

#view for change personal bio for users
def bio(request):

    account = request.user
    if request.method == 'POST':
        form = newBio(request.POST)
        if form.is_valid():
            bio = form.cleaned_data.get('bio')
            account.bio = bio
            account.save()
            return redirect('profile')
    else:
        form = newBio()
    return render(request, 'account/bio.html', {"form" : form })

