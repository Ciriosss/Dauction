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
from django.http import HttpResponseRedirect
import hashlib
import redis

#redis connection
client = redis.StrictRedis(host='127.0.0.1', port=6379, password='', db=0)

#home view

def home(request):
    return render(request, "auction/home.html", {})

# view where users can see all items related to a active auction
def items(request):
    categories =[ 'Tecnology','Clothes' ,'Real estate','Antiques','Sport','Other']
    items = []
    auctions = Auction.objects.all().order_by('-published')
    for auction in auctions:
        if not auction.is_expired() :
            items.append(Item.objects.get(id = auction.item.id))
    items = pagination(request, list=items, num = 3)
    return render(request, "auction/items.html", {'items':items, 'categories':categories})

#view that filter items acording category chosen by the user
def fiterByCategory(request, category):
    categories = ['Tecnology', 'Clothes', 'Real estate', 'Antiques', 'Sport', 'Other']
    items = Item.objects.filter(category = category)
    items = pagination(request, list=items, num = 3)
    return render(request, "auction/items.html", {'items': items, 'categories': categories})

#view for auctions
@login_required(login_url='login')
def auction(request, pk):
    item = Item.objects.get(pk = pk)
    auction = Auction.objects.get(item =item)
    bids = Bid.objects.filter(auction = auction).order_by('-datetime')
    account = request.user
    comments = Comment.objects.filter(auction = auction).order_by('-datetime')
    # bid form
    if request.method == 'POST':
        bidForm = newBid(request.POST)

        if bidForm.is_valid():
            amount = bidForm.cleaned_data.get('amount')
            lastBid = Bid.objects.filter(auction = auction).last()
            # check if the offer is higher than the last one
            if lastBid:
                if amount < lastBid.amount:
                    messages.warning(request, 'You have to make a higher offer than the last one')
                    return HttpResponseRedirect(request.path_info)
            else:
                # check if the offer is higher than the initial price
                if amount < auction.starterPrice :
                    messages.warning(request, 'You have to make a higher offer than the starter price')
                    return HttpResponseRedirect(request.path_info)
            #creation of new bid
            bid = Bid.objects.create(auction=auction, address=account.address, amount=amount)

            #insering data to redis db
            client.set(bid.id, "from {} to the auction {} with {} ETH in date:{}".format(bid.address,bid.auction.id, bid.amount, str(bid.datetime) ))

            messages.success(request, 'Bid correctly registred')
            return HttpResponseRedirect(request.path_info)
        #form for comments
        commentForm = newComment(request.POST)
        if commentForm.is_valid():
            comment = commentForm.cleaned_data.get('comment')

            Comment.objects.create(author = account,auction=auction, comment = comment)
            messages.success(request, 'Bid correctly registred')
            return HttpResponseRedirect(request.path_info)
    else:
        bidForm = newBid()
        commentForm = newComment()
    return render(request, "auction/auction.html", {'auction': auction, 'bids':bids, 'bidForm':bidForm, 'commentForm':commentForm, 'comments': comments})


#form for create a new auction
#this form require data about item and about auction

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
        image = request.FILES.get('image')
        seller = Account.objects.get(address = address)

        #chack if data are valid
        try:
            item = Item.objects.create(seller = account, category = category, name = name, description = description, image=image)
            Auction.objects.create(item = item, starterPrice = starterPrice,expiration = expiration, selleraddress = address, winner = seller)
            messages.success(request, 'Auction correctly registred')
            return redirect('items')
        except:

            messages.warning(request, 'Check your data, something went wrong!')
            return HttpResponseRedirect(request.path_info)
    else:

        return render(request, "auction/newAuction.html",{'account':account})

#view for all transactions
def transactions(request):
    transactions = Transaction.objects.all().order_by('-datetime')
    return render(request, 'auction/transactions.html', {"transactions": transactions})

#view for one single transaction
def transactionDetail(request,tx):
    transaction = Transaction.objects.get(tx = tx)
    return render(request, 'auction/transactionDetail.html', {'transaction': transaction})

# all auctions expired
def auctionsFinished(request):
    categories = ['Tecnology', 'Clothes', 'Real estate', 'Antiques', 'Sport', 'Other']
    items = []
    auctions = Auction.objects.all()
    for auction in auctions:
        if auction.is_expired() :
            items.append(auction.item)
    items = pagination(request, list=items, num=3)
    return render(request, 'auction/items.html', {'items':items,  'categories':categories})


"""
 fuctions that in backgroud automaticaly check if some auctions are expirated.
 
 if yes the function 
 1) determinate the winner bid and so the winner
 2) make the ETH transaction (from the winner to the seller)
 3) assign all values to the json field of the auction
 4) calculate the hash of the json field
 5) write it in a ETH transaction in my personal ETH ganache blockchain
 """

@background(schedule=10)
def checkExpiration():
    auctions = Auction.objects.filter(jsonResult = {})
    for auction in auctions:
        if auction.is_expired():
            winnerBid = Bid.objects.filter(auction=auction).last()
            if winnerBid:
                address = winnerBid.address
                auction.winner = Account.objects.get(address=address)

                tx = transferETH(auction.winner,auction.selleraddress,winnerBid.amount)
                Transaction.objects.create(addressFrom = auction.winner.address,addressTo = auction.selleraddress, amount = winnerBid.amount,tx=tx )


                bidDate = str(winnerBid.datetime)
                amount = winnerBid.amount

            else:
                auction.winner = Account.objects.get(address = auction.selleraddress)
                bidDate = False
                amount = auction.starterPrice

            publication = str(auction.published)
            expiration = str(auction.expiration)

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
                "Bid_amount": amount,
                "Bid_date": bidDate
            }

            auction.jsonResult = json.dumps(data)
            auction.jsonHash = hashlib.sha256(auction.jsonResult.encode('utf-8')).hexdigest()
            auction.txId = signedAuction(auction.jsonHash)
            auction.save()
            adminAddress ='0x6D5C772413f1E00C01F5803d970C72397a7A130b'
            Transaction.objects.create(addressFrom = adminAddress,addressTo = adminAddress, amount = 0,tx=auction.txId, jsonHash = auction.jsonHash)
checkExpiration()

