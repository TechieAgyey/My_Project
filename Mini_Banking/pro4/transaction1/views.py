#transaction1/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation
from django.db import transaction as db_transaction
from django.http import JsonResponse
from .models import SplitRequest

User = get_user_model()

@login_required(login_url='login')
def credit_view(request):
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount', 0))
            if amount <= 0:
                raise ValueError("Deposit amount must be greater than zero.")
            
            # Added "Self Deposit" description
            request.user.make_transaction(amount, 'CREDIT', description="Self Deposit")
            messages.success(request, f"Successfully deposited Rs.{amount:.2f}")
            return redirect('dashboard')
        except (ValueError, Decimal.InvalidOperation) as e:
            messages.error(request, str(e))
            
    return render(request, 'credit.html')

@login_required(login_url='login')
def debit_view(request):
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount', 0))
            if amount <= 0:
                raise ValueError("Withdrawal amount must be greater than zero.")
            
            # Added "Self Withdrawal" description
            request.user.make_transaction(amount, 'DEBIT', description="Self Withdrawal")
            messages.success(request, f"Successfully withdrew Rs.{amount:.2f}")
            return redirect('dashboard')
        except (ValueError, Decimal.InvalidOperation) as e:
            messages.error(request, str(e))
            
    return render(request, 'debit.html')

@login_required(login_url='login')
def transfer_view(request):
    if request.method == "POST":
        # Get data from transfer.html
        target_account_no = request.POST.get('recipient')
        typed_name = request.POST.get('recipient_name', '').strip().lower()
        
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            
            if amount <= 0:
                raise ValueError("Transfer amount must be greater than zero.")

            with transaction.atomic():
                # 1. Get sender and lock the row for safety
                sender = User.objects.select_for_update().get(pk=request.user.pk)
                
                # 2. Search by account_no (4-digit ID) 
                recipient = User.objects.select_for_update().filter(account_no=target_account_no).first()

                if not recipient:
                    raise ValueError(f"Account number '{target_account_no}' not found.")
                
                if recipient == sender:
                    raise ValueError("You cannot transfer money to yourself.")


                # 4. Check Balance
                if sender.balance < amount:
                    raise ValueError(f"Insufficient funds. Balance: Rs.{sender.balance:.2f}")

                # 5. Execute using your CustomUser's make_transaction method
                # This handles balance updates and log creation
                sender.make_transaction(amount, 'DEBIT', description=f"Transfer to {recipient.username} (A/C: {recipient.account_no})")
                recipient.make_transaction(amount, 'CREDIT', description=f"Received from {sender.username} (A/C: {sender.account_no})")

            messages.success(request, f"Successfully transferred Rs.{amount:.2f} to {recipient.first_name}")
            return redirect('dashboard')

        except (ValueError, InvalidOperation) as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "A technical error occurred during the transfer.")

    return render(request, 'transfer.html')


def get_recipient_name(request):
    account_no = request.GET.get('account_no')
    user = User.objects.filter(account_no=account_no).first()
    if user:
        # Returns the full name to the JavaScript
        return JsonResponse({
            'exists': True, 
            'name': f"{user.first_name} {user.last_name}".strip() or user.username
        })
    return JsonResponse({'exists': False})



@login_required(login_url='login')
def split_money(request):
    active_users = User.objects.exclude(id=request.user.id).filter(is_active=True)
    
    if request.method == "POST":
        try:
            total_amount = Decimal(request.POST.get('total_amount'))
            num_people = int(request.POST.get('num_people'))
            # Get the list of IDs from the checkboxes in your HTML
            selected_user_ids = request.POST.getlist('selected_users') 
            
            your_share = round(total_amount / num_people, 2)
            
            with db_transaction.atomic():
                user = User.objects.select_for_update().get(pk=request.user.pk)
                if user.balance < your_share:
                    raise ValueError(f"Insufficient funds. Your share: Rs.{your_share}")
                
                # 1. Deduct your share
                user.make_transaction(your_share, 'DEBIT', description=f"Paid Split Share (Total: Rs.{total_amount})")
                
                # 2. Create requests for the others
                for uid in selected_user_ids:
                    recipient = User.objects.get(id=uid)
                    SplitRequest.objects.create(
                        creator=request.user,
                        payer=recipient,
                        amount=your_share,
                        description=f"Split for Total: Rs.{total_amount}"
                    )
            
            messages.success(request, f"Paid your share of Rs.{your_share} and sent requests to {len(selected_user_ids)} people!")
            return redirect('dashboard')
            
        except (ValueError, InvalidOperation) as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, 'split.html', {'active_users': active_users})


@login_required(login_url='login')
def split_request(request):
    # Get requests where current user is the 'payer' and hasn't paid yet
    pending = SplitRequest.objects.filter(payer=request.user, is_paid=False).order_by('-timestamp')
    
    return render(request, 'split_request.html', {'pending_requests': pending})

@login_required(login_url='login')
def pay_split(request, request_id):
    if request.method == "POST":
        req = SplitRequest.objects.get(id=request_id)
        
        with db_transaction.atomic():
            payer = User.objects.select_for_update().get(pk=request.user.pk)
            creator = User.objects.select_for_update().get(pk=req.creator.pk)
            
            if payer.balance < req.amount:
                messages.error(request, "Insufficient balance to pay this request.")
                # Change 'view_requests' to 'split_request'
                return redirect('split_request') 
            
            # Execute Transaction
            payer.make_transaction(req.amount, 'DEBIT', description=f"Settled Split Bill to {creator.username}")
            creator.make_transaction(req.amount, 'CREDIT', description=f"Split Bill Repayment from {payer.username}")
            
            # Mark as paid
            req.is_paid = True
            req.save()
            
        messages.success(request, f"Paid Rs.{req.amount} to {creator.first_name} successfully!")
    
    # Change 'view_requests' to 'split_request'
    return redirect('split_request') 

