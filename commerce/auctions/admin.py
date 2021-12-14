from django.contrib import admin
from .models import Category, Listing, Bid, Watchlist, Comment
# Register your models here.
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Watchlist)
admin.site.register(Comment)