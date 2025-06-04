from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as django_logout
from blogapp.forms import CustomUserCreationForm
from .models import Post, Profile, Comment  # Import the Post, Profile, and Comment models

# Create your views here.

@login_required(login_url='login')
def index(request):
    username = request.user.username if request.user.is_authenticated else None
    blogs = Post.objects.filter(published=True).order_by('-created_at')
    print(f"Username: {username}")  # Debugging line to check username
    user_photo = request.user.profile.profile_image.url  
    print(f"User Photo: {user_photo}")  # Debugging line to check user photo
    return render(request, 'blogapp/index.html' , {
        'blogs': blogs,
        'username': username,
        'user_photo': user_photo
    }
)

def register(request):
    if request.method == 'POST': 
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()  # Save user first
            # Now create profile for this user
            Profile.objects.create(user=user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})



@login_required(login_url='login')
def profile(request):
    if request.user.is_authenticated:
        username = request.user.username
        profile = Profile.objects.filter(user=request.user).first()
        bio = profile.bio if profile else ''
        profile_image = profile.profile_image.url if profile and profile.profile_image else None
        return render(request, 'blogapp/profile.html', {'bio': bio, 'profile_image': profile_image, 'username': username})
    else:
        return redirect('login')  # Redirect to login if not authenticated


def logout(request):
 django_logout(request)
 return redirect('login')  # Redirect to login page after logout


def blog(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = post.comments.all()
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment = Comment(post=post, user=request.user, content=content)
            comment.save()
            return redirect('blog', post_id=post.id)
    return render(request, 'blogapp/blog.html', {'post': post, 'comments': comments})