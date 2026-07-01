# Message1/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from Chat1.models import Message, Notification 


User = get_user_model()

@login_required
def chat_screen(request, username):
    receiver = get_object_or_404(User, username=username)
    
    # 1. Handle sending a new message
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            # Create the message
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
            
            # Create a notification for the receiver
            Notification.objects.create(
                user=receiver,
                message=f"New message from {request.user.username}: {content[:30]}..."
            )
            # Redirect to the same page to prevent form resubmission on refresh
            return redirect('chat_screen', username=username)

    # 2. Fetch conversation history (ordered by oldest to newest)
    chat_messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) | 
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # 3. Mark messages sent TO the current user as read when they open this screen
    chat_messages.filter(receiver=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'chat.html', {
        'receiver': receiver, 
        'chat_messages': chat_messages
    })

@login_required
def notifications_view(request):
    # Fetch all notifications for the logged-in user, newest first
    notifications = request.user.notifications.all().order_by('-timestamp')
    
    # Mark unread notifications as read immediately upon viewing the page
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'notifications.html', {'notifications': notifications})
