import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.core.paginator import Paginator

from .models import User, Post, Followers, Likes

# To build profile page - make a class to hold data - then make url to point to this view and return json or otherwise 
# data to build the page - we stopped here 

class ProfileInfo():
    username =''
    follower_count =0
    following_count =0
    own_profile = False
    posts = []
    is_following = False
    
    def __init__(self, username, follower_count, following_count, posts, own_profile, is_following):
        self.username  = username
        self.follower_count  = follower_count
        self.following_count  = following_count
        self.posts = posts
        self.own_profile = own_profile
        self.is_following = is_following


def index(request):
    return render(request, "network/index.html")


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
@login_required
def post(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    content = data.get("content","").strip()

    if content.len() == 0:
        return JsonResponse({"error": "No text has been entered"}, status=400)

    this_post = Post(
        content=content, 
        user=request.user
        )
    this_post.save()

    return JsonResponse({"message": "Post saved successfully."}, status=201)

	
@login_required
def post_update(request):

	if request.method != "PUT":
		return JsonResponse({"error": "PUT request required."}, status=400)

	data = json.loads(request.body)
	postid = data.get("postid")
	content = data.get("content")
	
	try:
		post = Post.objects.get(pk=postid)
	except Post.DoesNotExist:
		return JsonResponse({"error": "Post not found."}, status=404)
   
	post.content = content
	post.save()

	return JsonResponse(post.serialize())

def get_page_obj (datalist, request): 
    paginator = Paginator (datalist, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

def index(request):
    posts = Post.objects.all() 
    posts = posts.order_by("-created_at")
    page_obj = get_page_obj(posts, request)
    return render(request, 'network/index.html', {'page_obj': page_obj})
    

@csrf_exempt
@login_required
def following_count(request): 
    followers = Followers.objects.filter(following=request.user.id).count()

    following = Followers.objects.filter(user=request.user.id).count()
    return JsonResponse({'followers':followers, 'following':following}, status=404)


# Returns only the posts of the people you follow
@login_required
def followed_users_posts(request): 
    followed_users = Followers.objects.filter(user=request.user.id).values('following')
    posts = Post.objects.filter(user__in=followed_users)
    posts = posts.order_by("-created_at")
    
    page_obj = get_page_obj(posts, request)
    return render(request, 'network/following.html', {'page_obj': page_obj})
    

@login_required
def is_following(request, userid): 

    count = Followers.objects.filter(user=request.user.id, following=userid)
    if count == 1: 
        return True 
    else: 
        return False

# function call to return posts by a user
def user_posts(userid): 
    posts = Post.objects.filter(user=userid)
    posts = posts.order_by("-created_at")
    return posts

@login_required
def get_post_content(request, postid): 
    post = Post.objects.get(int(id=postid))
    content = post.content
    return content

def profile(request, user_id): 
    posts = user_posts(user_id)
    followers = Followers.objects.filter(following=user_id).count()
    following = Followers.objects.filter(user=user_id).count()
    is_following = False
    own_profile = False
    if (request.user.id == user_id):
        own_profile = True

    # If the user is logged in then check if the signed in user follows this user
    if request.user.is_authenticated:
        count = Followers.objects.filter(user=request.user.id, following=user_id).count()
        if count > 0: 
            is_following = True 
    profile_user = User.objects.filter(pk=user_id) 
    profile_user_username = profile_user[0].username
	
    page_obj = get_page_obj(posts, request)
    return render(request, 'network/profile.html', {'page_obj': page_obj,
                            "profile_info" : ProfileInfo(profile_user_username, followers, following, posts,own_profile,  is_following)})

@login_required
@csrf_exempt
def change_following_status (request, user_id):
    new_status =''
    data = json.loads(request.body)
    if data.get("new_status") is not None:
        new_status = data["new_status"]

    follower = Followers.objects.filter(user=request.user.id, following=user_id)
    followers = follower.count()
    if followers > 0: 
        if (new_status == "unfollow"):
            follower.delete()
            followers -= 1
    elif (new_status == "follow"):
            new_follower = Followers(user = User.objects.get(pk=request.user.id),
                            following = User.objects.get(pk=user_id))
                                     
            new_follower.save()
            followers += 1
            
    following = Followers.objects.filter(user=user_id).count()

    return JsonResponse({'followers':followers, 'following':following}, status=201)

	
@login_required
@csrf_exempt
def like_update (request, postid):
	    
    like = Likes.objects.filter(user=request.user.id, post=postid)
    like_count = like.count()
    if like_count > 0: 
	    like.delete()
    else:
	    new_like = Likes(user = User.objects.get(pk=request.user.id),
                        post = Post.objects.get(pk=postid))
                                     
	    new_like.save()
            
    likes = Likes.objects.filter(post=postid).count()
	
    post = Post.objects.get(pk=postid)
    post.likes_count = likes
	   
    post.save()

    return JsonResponse({'likes':likes}, status=201)


