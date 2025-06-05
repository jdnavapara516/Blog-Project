from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as django_logout
from blogapp.forms import CustomUserCreationForm
from .models import Category, Contact, Like, Post, Profile, Comment  # Import the Post, Profile, and Comment models

# Create your views here.

def get_user_profile_photo(user):
    try:
       profile = Profile.objects.get(user=user)
       return profile.profile_image
    except Profile.DoesNotExist:
        return None

@login_required(login_url='login')
def index(request):
    username = request.user.username if request.user.is_authenticated else None
    blogs = Post.objects.filter(published=True).order_by('-created_at')
    print(f"Username: {username}")  # Debugging line to check username
    user_photo = get_user_profile_photo(request.user) 
    like = Like.objects.filter(user=request.user) if request.user.is_authenticated else None
    
    
    print(f"User Photo: {user_photo}")  # Debugging line to check user photo
    return render(request, 'blogapp/index.html' , {
        'blogs': blogs,
        'username': username,
        'user_photo': user_photo,
        
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
    comments = post.comments.order_by('-created_at')  # Fetch comments for the post, ordered by creation time
    
    author_photo = get_user_profile_photo(post.author)  # Get author's profile photo
    print(f"Author Photo: {author_photo}")  # Debugging line to check author photo
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment = Comment(post=post, user=request.user, content=content)
            comment.save()
            return redirect('blog', post_id=post.id)
    user_photo = get_user_profile_photo(request.user)  # Get user profile photo
    photo_list = []
    for comment in comments:
        photo = get_user_profile_photo(comment.user)
        if photo:
            photo_list.append(photo)
        else:
            photo_list.append(None)
    comment_data = zip(comments, photo_list)
    print("bio : " + str(post.author.profile.bio))
    return render(request, 'blogapp/blog.html', {'post': post, 'comments': comments, 'user_photo': user_photo, 'author_photo': author_photo, 'photo_list': photo_list , 'comment_data': comment_data})



def new_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        print(f"Content: {content}")
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(post=post, user=request.user, content=content)
        return redirect('blog', post_id=post.id)  # Redirect to the blog post page after adding comment
    return redirect('index')  # Redirect to index if not a POST request


def like(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user.is_authenticated:
        like, created = post.likes.get_or_create(user=request.user)
        if not created:
            like.delete()  # If the like already exists, remove it
        return redirect('blog', post_id=post.id)  # Redirect to the blog post page after liking/unliking
    return redirect('login')  # Redirect to login if user is not authenticated


@login_required(login_url='login')
def myblog(request):
    if request.user.is_authenticated:
        username = request.user.username
        user_photo = get_user_profile_photo(request.user)
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        return render(request, 'blogapp/myblog.html', {'posts': posts, 'username': username, 'user_photo': user_photo})
    
@login_required(login_url='login')
def contact(request):
    user_phhoto = get_user_profile_photo(request.user) if request.user.is_authenticated else None
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        new_mgs = Contact(name=name, email=email, message=message)
        new_mgs.save()  # Save the contact message to the database
       
        # Here you can add logic to save the contact message or send an email
        print(f"Contact Form Submitted: {name}, {email}, {message}")
        return redirect('index')
    else:
        # Render the contact form
        return render(request, 'blogapp/contact.html', {'user_photo': user_phhoto})
    
@login_required(login_url='login')
def createblog(request):
    user_photo = get_user_profile_photo(request.user) if request.user.is_authenticated else None
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id) if category_id else None
        post = Post.objects.create(
            title=title,
            author=request.user,
            content=content,
            image=image,
            category=category
        )
        post.save()
        return redirect('myblog')  # Redirect to the user's blog page after creating a new post
    else:
        categories = Category.objects.all()
        return render(request, 'blogapp/createblog.html', {'categories': categories, 'user_photo': user_photo})
    

@login_required(login_url='login')
def updateblog(request, post_id):
    post = Post.objects.get(id=post_id)
    user_photo = get_user_profile_photo(request.user) if request.user.is_authenticated else None
    if request.method == 'POST':
        Post.objects.filter(id=post_id).update(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            image=request.FILES.get('image', post.image),  # Use existing image if no new one is uploaded
            category=Category.objects.get(id=request.POST.get('category')) if request.POST.get('category') else None
        )
        return redirect('myblog')
    else:
        categories = Category.objects.all()
        return render(request, 'blogapp/updateblog.html', {
            'post': post,
            'categories': categories,
            'user_photo': user_photo
        })