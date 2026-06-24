# transaction1/urls.py
from django.urls import path
from transaction1 import views as trans_views
from . import views

urlpatterns = [
    path('credit/', views.credit_view, name='credit_view'), # This name must match the template
    path('debit/', views.debit_view, name='debit_view'),   # This name must match the template
    path('transfer/', views.transfer_view, name='transfer_view'),
    path('split/', views.split_money, name='split_money'),
    # In your urls.py
    path('get-recipient-name/', views.get_recipient_name, name='get_recipient_name'),
    path('split_request/', views.split_request, name='split_request'),
    path('pay-split/<int:request_id>/', views.pay_split, name='pay_split'),


]
