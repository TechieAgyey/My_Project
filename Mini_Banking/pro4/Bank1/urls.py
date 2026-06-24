from django.urls import path
from . import views
from transaction1 import views as trans_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # This makes it the home page
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_details_view, name='account_details'),

    
]