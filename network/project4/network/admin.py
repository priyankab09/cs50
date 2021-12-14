from django.contrib import admin
from .models import Post, Followers, Likes

# Register your models here.
admin.site.register(Post)
admin.site.register(Followers)
admin.site.register(Likes)