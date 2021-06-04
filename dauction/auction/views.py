from django.shortcuts import render, redirect
from .models import Item, Auction, Bid, Comment
from django.contrib import messages
from account.forms import newBid, newComment
from background_task import background
import json
from django.contrib.auth.decorators import login_required
from account.models import Account, Transaction
from .blockchain import transferETH, signedAuction
from .utils import pagination
import hashlib
import redis

client = redis.StrictRedis(host='127.0.0.1', port=6379, password='', db=0)


def home(request):
    return render(request, "auction/home.html", {})

def items(request):
    categories =[ 'Tecnology','Clothes' ,'Real estate','Antiques','Sport','Other']
    items = []
    auctions = Auction.objects.all()
    for auction in auctions:
        if not auction.is_expired() :
            items.append(Item.objects.get(id = auction.item.id))
    items = pagination(request, list=items, num = 3)
    return render(request, "auction/items.html", {'items':items, 'categories':categories})

def fiterByCategory(request, category):
    categories = ['Tecnology', 'Clothes', 'Real estate', 'Antiques', 'Sport', 'Other']
    items = Item.objects.filter(category = category)
    items = pagination(request, list=items, num = 3)
    return render(request, "auction/items.html", {'items': items, 'categories': categories})

@login_required(login_url='login')
def auction(request, pk):
    item = Item.objects.get(pk = pk)
    auction = Auction.objects.get(item =item)
    bids = Bid.objects.filter(auction = auction).order_by('-date')
    account = request.user
    comments = Comment.objects.filter(auction = auction)
    if request.method == 'POST':
        bidForm = newBid(request.POST)

        if bidForm.is_valid():
            amount = bidForm.cleaned_data.get('amount')
            lastBid = Bid.objects.filter(auction = auction).last()
            if lastBid:
                if amount < lastBid.amount:
                    messages.warning(request, 'You have to make a higher offer than the last one')
                    return redirect('items')
            else:
                if amount < auction.starterPrice :
                    messages.warning(request, 'You have to make a higher offer than the last one')
                    return redirect('items')

            Bid.objects.create(auction=auction, address=account.address, amount=amount)
            client.rpush(f"{account.address}", f"{amount}")

            messages.success(request, 'Bid correctly registred')
            return redirect('items')

        commentForm = newComment(request.POST)
        if commentForm.is_valid():
            comment = commentForm.cleaned_data.get('comment')


            Comment.objects.create(author = account,auction=auction, comment = comment)
            messages.success(request, 'Bid correctly registred')
            return redirect('items')
    else:
        bidForm = newBid()
        commentForm = newComment()
    return render(request, "auction/auction.html", {'auction': auction, 'bids':bids, 'bidForm':bidForm, 'commentForm':commentForm, 'comments': comments})

@login_required(login_url='login')
def newAuction(request):

    account = request.user
    if request.method == 'POST':
        category = request.POST.get('category')
        name = request.POST.get('name')
        description = request.POST.get('description')
        starterPrice = request.POST.get('starterPrice')
        expiration = request.POST.get('expiration')
        address = request.POST.get('address')
        image = request.POST.get('image')

        seller = Account.objects.get(address = address)

        item = Item.objects.create(seller = account, category = category, name = name, description = description, image=image)
        Auction.objects.create(item = item, starterPrice = starterPrice,expiration = expiration, selleraddress = address, winner = seller)

        messages.success(request, 'Auction correctly registred')
        return redirect('items')
    else:

        return render(request, "auction/newAuction.html",{'account':account})

def transactions(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'auction/transactions.html', {"transactions": transactions})

def transactionDetail(request,tx):
    transaction = Transaction.objects.get(tx = tx)
    return render(request, 'auction/transactionDetail.html', {'transaction': transaction})


def auctionsFinished(request):
    items = []
    auctions = Auction.objects.all()
    for auction in auctions:
        if auction.is_expired() :
            items.append(auction.item)
    items = pagination(request, list=items, num=3)
    return render(request, 'auction/items.html', {'items':items})

@background(schedule=60)
def checkExpiration():
    auctions = Auction.objects.filter(jsonResult = {})
    for auction in auctions:
        if auction.is_expired():
            winnerBid = Bid.objects.filter(auction=auction).last()
            address = winnerBid.address
            auction.winner = Account.objects.get(address=address)

            tx = transferETH(auction.winner,auction.selleraddress,winnerBid.amount)
            Transaction.objects.create(addressFrom = auction.winner.address,addressTo = auction.selleraddress, amount = winnerBid.amount,tx=tx )

            publication = str(auction.published)
            expiration = str(auction.expiration)
            bidDate = str(winnerBid.date)

            data = {
                "Auction_id": auction.id,
                "Item_id": auction.item.id,
                "Item_name": auction.item.name,
                "Item_description": auction.item.description,
                "Starter_price": auction.starterPrice,
                "Publication_date": publication,
                "Expiration_date": expiration,
                "Winner": auction.winner.first_name,
                "Winner_address": auction.winner.address,
                "Bid_amount": winnerBid.amount,
                "Bid_date": bidDate

            }
            auction.jsonResult = json.dumps(data)
            auction.jsonHash = hashlib.sha256(auction.jsonResult.encode('utf-8')).hexdigest()
            auction.txId = signedAuction(auction.jsonHash)
            auction.save()

checkExpiration()

