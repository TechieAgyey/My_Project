import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Post, Comment

# --- USER AUTHENTICATION ---

def register(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        if u and p:
            try:
                # Runs validators from settings.py (like MinimumLengthValidator)
                validate_password(p, user=User(username=u))
                
                if User.objects.filter(username=u).exists():
                    messages.error(request, "Username already taken!")
                else:
                    new_user = User.objects.create_user(username=u, password=p)
                    login(request, new_user)
                    messages.success(request, f"Welcome to Bloggers, {u}!")
                    return redirect('feed')
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
    return render(request, 'register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {u}!")
            return redirect('feed')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('register')

# --- MAIN FEED & POSTING ---

@csrf_protect
def feed(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to participate.")
            return redirect('login')

        # 1. Create a New Post
        if 'message' in request.POST:
            msg = request.POST.get('message')
            if msg:
                Post.objects.create(author=request.user, message=msg)
                messages.success(request, "Post shared!")

        # 2. Create a New Comment or Reply
        elif 'comment_text' in request.POST:
            post_id = request.POST.get('post_id')
            parent_id = request.POST.get('parent_id') # For nested replies
            text = request.POST.get('comment_text')
            
            post_obj = get_object_or_404(Post, id=post_id)
            parent_obj = Comment.objects.filter(id=parent_id).first() if parent_id else None

            if text:
                new_comment = Comment.objects.create(
                    post=post_obj, 
                    author=request.user, 
                    text=text, 
                    parent=parent_obj
                )
                
                # Logic for Tagging (@username)
                tags = re.findall(r'@(\w+)', text)
                for username in tags:
                    tagged_user = User.objects.filter(username=username).first()
                    if tagged_user:
                        new_comment.tagged_users.add(tagged_user)
                
                messages.success(request, "Comment added.")

        return redirect('feed')

    # Prefetch profiles and comments to keep the site fast
    all_posts = Post.objects.all().prefetch_related('comments__author__profile', 'comments__replies').order_by('-created_at')
    return render(request, 'feed.html', {'posts': all_posts})

# --- INTERACTION & VISIBILITY ---

def like_post(request, pk):
    if not request.user.is_authenticated:
        messages.info(request, "Log in to like posts.")
        return redirect('register')
        
    post = get_object_or_404(Post, id=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('feed')

@login_required
def toggle_comment_visibility(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # Only comment author or post owner can hide
    if request.user == comment.author or request.user == comment.post.author:
        comment.is_hidden = not comment.is_hidden
        comment.save()
        messages.success(request, "Visibility updated.")
    else:
        messages.error(request, "Permission denied.")
    return redirect('feed')

# --- USER DASHBOARD (MY POSTS) ---

@login_required
def dashboard(request):
    my_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'posts': my_posts})

# --- EDIT & DELETE (CRUD) ---

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        new_msg = request.POST.get('message')
        if new_msg:
            post.message = new_msg
            post.save()
            messages.success(request, "Post updated!")
            return redirect('dashboard')
    return render(request, 'edit_post.html', {'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('dashboard')
    return render(request, 'delete_confirm.html', {'post': post})
