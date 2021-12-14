
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.followed_users_posts, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"), 
    # path("posts", views.all_posts, name="posts"),
    path("posts/<int:user_id>", views.user_posts, name="this_users_posts"), 
    path("profile/<int:user_id>", views.profile, name="profile"), 
    path("change_following_status/<int:user_id>", views.change_following_status, name="change_following_status"),
    path("post_update", views.post_update, name="post_update"),
    path("like_update/<int:postid>", views.like_update, name="like_update") 

]
