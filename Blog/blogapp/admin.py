from django.contrib import admin
from .models import Category, Post, Comment, Like, Profile

# Register your models here.

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Profile)



