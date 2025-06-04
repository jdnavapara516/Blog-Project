from django.shortcuts import render
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path("blog/<int:post_id>/", views.blog, name='blog'),  # Assuming you have a post_detail view
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
