#Message1 urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('chat/<str:username>/', views.chat_screen, name='chat_screen'),
    path('notifications/', views.notifications_view, name='notifications'),
]
