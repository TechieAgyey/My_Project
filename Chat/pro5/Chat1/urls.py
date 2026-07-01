from django.urls import path, include # CHANGE: Added include
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('add-friend/<int:user_id>/', views.add_friend, name='add_friend'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('chats/', views.recent_chats, name='recent_chats'),
    
    # CHANGE: Included Message1 URLs so chat_screen becomes accessible
    path('message/', include('Message1.urls')), 
]