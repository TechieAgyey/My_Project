from django.contrib import admin
from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.feed, name="feed"),
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('logout/', views.logout_view, name="logout"),
    path('like/<int:pk>/', views.like_post, name='like_post'),
    path('edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('toggle-comment/<int:pk>/', views.toggle_comment_visibility, name='toggle_comment'),
]

# IMPORTANT: This allows Django to serve profile pictures during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
