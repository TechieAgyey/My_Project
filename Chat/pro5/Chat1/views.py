# chat1/views.py

# chat1/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# 1. FIX: Get the User model once globally
User = get_user_model()

@login_required
def chat_screen(request, username):
    # 2. FIX: 'User' is now defined above, so this won't crash
    receiver = get_object_or_404(User, username=username)
    
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
            
            Notification.objects.create(
                user=receiver, 
                message=f"New message from {request.user.username}",
                is_read=False
            )
            return redirect('chat_screen', username=username)

    chat_messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) | 
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')

    Message.objects.filter(sender=receiver, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'chat.html', {
        'receiver': receiver,
        'chat_messages': chat_messages
    })

@login_required
def recent_chats(request):
    # Logic for finding users you have talked to
    sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    
    chat_user_ids = set(list(sent_to) + list(received_from))
    chat_users = User.objects.filter(id__in=chat_user_ids)

    recent_list = []
    for user in chat_users:
        last_msg = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) | 
            (Q(sender=user) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        
        if last_msg:
            recent_list.append({
                'user': user,
                'last_message': last_msg
            })

    recent_list.sort(key=lambda x: x['last_message'].timestamp, reverse=True)
    return render(request, 'recent_chats.html', {'recent_list': recent_list})


def home(request):
    return render(request, 'home.html')

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'user_list.html', {'users': users})

@login_required
def add_friend(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    # Using the ManyToMany field 'friends' as per your template logic
    request.user.friends.add(friend)
    messages.success(request, f"You are now friends with {friend.username}!")
    return redirect('user_list')

@login_required
def remove_friend(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    request.user.friends.remove(friend)
    return redirect('user_list')

def login(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)

        if user is not None:
            auth_login(request, user)
            return redirect('recent_chats') 
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        email = request.POST.get('email')
        p_word = request.POST.get('password')

        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html')
        
        new_user = User.objects.create_user(username=u_name, email=email, password=p_word)
        auth_login(request, new_user) # Log them in immediately after signup
        return redirect('recent_chats')
    return render(request, 'signup.html')

def logout_user(request):
    auth_logout(request)
    return redirect('login')

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all().order_by('-timestamp')
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})

def notification_count(request):
    if request.user.is_authenticated:
        return {'unread_count': request.user.notifications.filter(is_read=False).count()}
    return {'unread_count': 0}

# Optional: Using FriendRequest model if you decide to use 'Pending' logic
@login_required
def send_friend_request(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    # Ensure FriendRequest is imported in models
    # FriendRequest.objects.get_or_create(from_user=request.user, to_user=target_user)
    return redirect('user_list')
