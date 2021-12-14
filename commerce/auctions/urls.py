from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addlisting", views.add_listing, name="add"),
    path("listing/<int:listing_id>", views.listing, name="listing"), 
    path("listing/<int:listing_id>/<str:message>", views.listing, name="listing"), 
    path("bid", views.bid, name="bid"),
    path("comment", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("close", views.close_auction, name="close")
]
