from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Max
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import User, Category, Listing, Bid, Watchlist, Comment

class ListingForm(forms.Form): 
    title = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control listing-title', 'placeholder':'Title'}))
    description = forms.CharField(label='', widget=forms.Textarea(attrs={'class': 'form-control listing-desc', 'rows': 3, 'cols': 30, 'placeholder':'Description'}))
    starting_bid = forms.DecimalField(label='', widget=forms.TextInput(attrs={'class': 'form-control listing-bid', 'placeholder':'Starting Bid'}))
    photo_url = forms.URLField(label = '', required=False, widget=forms.TextInput(attrs={'class': 'form-control listing-url', 'placeholder':'Image URL'}))

class BidForm(forms.Form):
    listing_id = forms.CharField(widget = forms.HiddenInput())
    bid = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Bid'}), label='')

    def clean(self):
        listing_id_val = int(self.cleaned_data['listing_id'])
        bid_val = self.cleaned_data['bid']
        starting_bid = Listing.objects.get(pk = listing_id_val).starting_bid
        max_bid = Bid.objects.filter(listing_id=listing_id_val).aggregate(Max('amount'))['amount__max'] or Decimal('0')
        if (bid_val <= starting_bid) or (bid_val <= max_bid):
           raise ValidationError ("Your bid should be higher than the current price.")
        
        return self.cleaned_data

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Comment'}), label='')
    listing_id = forms.CharField(widget = forms.HiddenInput())

class WatchlistForm(forms.Form):
    listing_id = forms.CharField(widget = forms.HiddenInput())

class CloseForm(forms.Form):
     listing_id = forms.CharField(widget = forms.HiddenInput())

class ListingInfo():
    listing =None
    current_price = 0
    bid_count = 0

    def __init__(self, listing, current_price, bid_count):
        self.listing  = listing
        self.current_price = current_price
        self.bid_count = bid_count

def get_additional_listing_info(listings):
    listings_info = []
    for listing in listings:
        bids = Bid.objects.filter(listing_id=listing.id)
        current_price = bids.aggregate(Max('amount'))['amount__max'] or Decimal('0')
        if (current_price < listing.starting_bid):
            current_price = listing.starting_bid
        bid_count = bids.count()
        listings_info.append (ListingInfo (listing, current_price, bid_count))
    
    return listings_info

def get_winning_bidder(listing_id):
    bid = Bid.objects.filter(listing_id=listing_id).order_by('-amount').first()
    if bid is not None:
        return bid.user_id 
    else: 
        return None


def index(request):
    listings = Listing.objects.filter(open=True)
    
    return render(request, "auctions/index.html", {
        "listings_info" : get_additional_listing_info(listings)
        })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def add_listing(request):
    if request.method == "GET":
        return render(request, "auctions/createlisting.html", {
            "listing": ListingForm(),
            "categories": Category.objects.all()
            })

    if request.method == "POST":
        form = ListingForm(request.POST)
        category_id = int(request.POST["categories"])
   
        if form.is_valid():
            listing = Listing(title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                starting_bid = form.cleaned_data["starting_bid"],
                photo_url = form.cleaned_data["photo_url"],
                # category = Category.objects.get(pk=int(request.POST["categories"])),                
                category = Category.objects.get(pk=category_id) if category_id > 0 else None,
                listed_by = User.objects.get(pk=request.user.id),
                open=True
                )
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        else:
            return render (request, "auctions/createlisting.html", {
                "form": form
                })
        
    
def listing(request, listing_id, message=""):
    listing = Listing.objects.get(pk=listing_id)
    bid_form = BidForm(initial= {"listing_id" : listing_id})
    close_form = CloseForm(initial= {"listing_id" : listing_id})
    comment_form = CommentForm(initial = {"listing_id" : listing_id})
    watchlist_form = WatchlistForm(initial = {"listing_id" : listing_id})

    bids = Bid.objects.filter(listing_id=listing_id)
    highest_bid = bids.aggregate(Max('amount'))['amount__max'] or Decimal('0')
    if highest_bid > listing.starting_bid:
        current_price = highest_bid 
    else: 
        current_price = listing.starting_bid

    bid_count = bids.count()

    watchlist_count = Watchlist.objects.filter(listing_id=listing_id, user=request.user.id).count()
    
    user_owner = True if listing.listed_by == request.user.id else False
    if not listing.open and request.user.id == get_winning_bidder(listing_id):
        bid_winner = True
    else: 
        bid_winner = False

    if request.method == "GET":
        return render(request, "auctions/listing.html", {
            "listing" : listing, 
            "bid_form" : bid_form,
            "comment_form" : comment_form,
            "watchlist_form" : watchlist_form,            
            "comments" : Comment.objects.filter(listing_id=int(listing_id)).order_by('-created_at'),
            "current_price" : current_price,
            "bid_count": bid_count,
            "watchlist_count" : watchlist_count,
            "user_owner" : user_owner,
            "bid_winner" : bid_winner,
            "close_form" : close_form,
            "message" : message
            }) 


@login_required(login_url='/login')
def bid(request):
    if request.method == "POST":
       form = BidForm(request.POST)
       listing_id = ""
       print (listing_id)
       if form.is_valid():
           bidval = form.cleaned_data["bid"]
           listing_id = form.cleaned_data["listing_id"]
          # highest_bid = Listing.objects.get(pk=starting_bid)
           bid = Bid(listing = Listing.objects.get(pk=int(listing_id)),
                      user = User.objects.get(pk=request.user.id),
                      amount = float(bidval) 
                      )
           bid.save()
           return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
       else:
            message = 'Error: '
            listing_id = form.cleaned_data["listing_id"]
            message = message + form.errors["__all__"][0]
            return HttpResponseRedirect(reverse("listing", args=(listing_id, message,)))

@login_required(login_url='/login')
def comment(request):
    if request.method == "POST":
       form = CommentForm(request.POST)
       if form.is_valid():
           comment = form.cleaned_data["comment"]
           listing_id = form.cleaned_data["listing_id"]
           comment = Comment(listing = Listing.objects.get(pk=int(listing_id)),
                      user = User.objects.get(pk=request.user.id),
                      comment = comment
                      )
           comment.save()
           return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
       else:
            message = 'Error: '
            listing_id = form.cleaned_data["listing_id"]
            message = message + form.errors["__all__"][0]
            return HttpResponseRedirect(reverse("listing", args=(listing_id, message,)))

@login_required(login_url='/login')
def watchlist(request): 
    if request.method == "GET":
        watched_listings = Watchlist.objects.filter(user_id=request.user.id)
        listings=[]

        for watched_listing in watched_listings:
            listings.append(Listing.objects.get(pk=int(watched_listing.listing_id)))

        return render(request, "auctions/watchlist.html", {
            "listings_info" : get_additional_listing_info(listings)
            })

    if request.method == "POST":
       form = WatchlistForm(request.POST)
       if form.is_valid():
           listing_id = form.cleaned_data["listing_id"]
           if request.POST.get("add_to_watchlist"):
               watchlist_item = Watchlist(listing = Listing.objects.get(pk=int(listing_id)), 
                                     user = User.objects.get(pk=request.user.id))
               watchlist_item.save()
           else:
               watchlist_item = Watchlist.objects.get(listing_id=listing_id, user_id=request.user.id)
               watchlist_item.delete()
           return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
       else:
            message = 'Error: '
            listing_id = form.cleaned_data["listing_id"]
            message = message + form.errors["__all__"][0]
            return HttpResponseRedirect(reverse("listing", args=(listing_id, message,)))

def categories(request):
    categories = Category.objects.all()
    return render (request, "auctions/categories.html", {
        "categories" : categories 
        })

def category(request, category_id):
    category = Category.objects.get(pk=int(category_id))
    category_items = Listing.objects.filter(category_id=category_id, open=True)  
    return render(request, "auctions/category.html", {
        "category" : category,
        "listings_info" : get_additional_listing_info(category_items)
        })


@login_required(login_url='/login')
def close_auction(request):
    message = ""
    noerrors = False
   
    if request.method == "POST":
       form = CloseForm(request.POST)
       if form.is_valid():
             listing_id = form.cleaned_data["listing_id"]
             listing = Listing.objects.get(pk=int(listing_id))
             if (not request.user.id == listing.listed_by_id):
                 message = 'Only the owner of the listing can close it'
             elif (listing.open == False):
                 message = 'Auction for this listing is already closed'
             else:                
                 listing.open = False
                 listing.save()
                 return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

             return HttpResponseRedirect(reverse("listing", args=(listing_id, message,)))
       else: 
            message = 'Error: '
            listing_id = form.cleaned_data["listing_id"]
            message = message + form.errors["__all__"][0]
            return HttpResponseRedirect(reverse("listing", args=(listing_id, message,)))
             

   
     

