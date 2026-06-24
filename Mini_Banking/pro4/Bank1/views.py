from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction
from transaction1.models import Transaction
from transaction1.models import SplitRequest

User = get_user_model()

@login_required(login_url='login')
def dashboard(request):
    # Fetch all transactions for the user, newest first
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')

    # Get latest single objects for the 'Ref' timestamps in your HTML cards
    last_credit = transactions.filter(transaction_type='CREDIT').first()
    last_debit = transactions.filter(transaction_type='DEBIT').first()

    # Calculate totals for the green/red cards
    credited = transactions.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0.00
    debited = transactions.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0.00

    # Count pending split requests for the logged-in user
    request_count = SplitRequest.objects.filter(payer=request.user, is_paid=False).count()

    context = {
        'user': request.user,
        'account_no': request.user.account_no, 
        'balance': request.user.balance,
        'credited': credited,
        'debited': debited,
        'last_credit': last_credit,
        'last_debit': last_debit,
        'transactions': transactions,
        'request_count': request_count,  # Added to context
    }
    return render(request, 'dashboard.html', context)

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        uname = request.POST.get('username')
        passw = request.POST.get('password')

        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        with transaction.atomic():
            user = User.objects.create_user(
                username=uname, 
                password=passw, 
                first_name=fname, 
                last_name=lname,
                balance=0.00  
            )

        auth_login(request, user)
        messages.success(request, f"Welcome, {uname}! Your account was created.")
        # Updated redirect to show account details first
        return redirect('account_details')
        
    return render(request, 'signup.html')

@login_required(login_url='login')
def account_details_view(request):
    return render(request, 'account_no.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        uname = request.POST.get('username')
        passw = request.POST.get('password')
        
        user = authenticate(request, username=uname, password=passw)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

