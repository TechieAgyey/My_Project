# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FriendRequest, Notification

@receiver(post_save, sender=FriendRequest)
def create_friend_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.to_user,
            notification_type='friend_request',
            message=f"{instance.from_user.username} sent you a friend request!"
        )
