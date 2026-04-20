
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ContactMessage, Service, BlogPost, UserProfile, Subscriber
from .forms import RegisterForm, UserProfileForm, BlogPostForm

# Home Page
def home(request):
    services = Service.objects.all()[:6]
    latest_posts = BlogPost.objects.filter(is_published=True)[:3]
    context = {
        'services': services,
        'posts': latest_posts,
    }
    return render(request, 'core/home.html', context)

# About Page
def about(request):
    return render(request, 'core/about.html')

# Services Page
def services(request):
    services = Service.objects.all()
    paginator = Paginator(services, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/services.html', {'services': page_obj})

# Blog Pages
def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/blog_list.html', {'posts': page_obj, 'search': search_query})
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views += 1
    post.save()
    return render(request, 'core/blog_detail.html', {'post': post})

# Contact Page
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('core:contact')  # ✅ Yeh correct hai

    
    return render(request, 'core/contact.html')

# Newsletter Subscription
def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, 'Successfully subscribed to newsletter!')
    return redirect('core:home')


# Authentication Views
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'core/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('home')

# Dashboard (Protected)
@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    context = {
        'profile': user_profile,
        'user': request.user,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def my_messages(request):
    messages_list = ContactMessage.objects.filter(email=request.user.email)
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/my_messages.html', {'messages': page_obj})


# def blog_list(request):
#     from django.http import HttpResponse
#     return HttpResponse("""
#         <h1>Blog Page Working!</h1>
#         <p>If you see this, the URL is correct.</p>
#         <p>Template issue: blog_list.html not found.</p>
#         <p>Template path should be: core/templates/core/blog_list.html</p>
#     """)


def blog_list(request):
    from django.http import HttpResponse
    from .models import BlogPost
    
    posts = BlogPost.objects.filter(is_published=True)
    
    html = '<h1>Blog Posts</h1>'
    for post in posts:
        html += f'<h2>{post.title}</h2><p>{post.content[:100]}</p><hr>'
    
    if not posts:
        html += '<p>No posts yet. Create one from admin panel.</p>'
    
    return HttpResponse(html)