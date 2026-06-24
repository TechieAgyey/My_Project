import random
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from transaction1.models import Transaction

class CustomUser(AbstractUser):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    account_no = models.CharField(max_length=4, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.account_no:
            while True:
                new_acc = str(random.randint(1000, 9999))
                if not CustomUser.objects.filter(account_no=new_acc).exists():
                    self.account_no = new_acc
                    break
        super().save(*args, **kwargs)

    def make_transaction(self, amount, t_type, description=""):
        with transaction.atomic():
            if t_type == 'DEBIT':
                if self.balance < amount:
                    raise ValueError("Insufficient balance")
                self.balance -= amount
            else:
                self.balance += amount
            
            self.save()
            
            # Pass account_no to the Transaction record
            Transaction.objects.create(
                user=self, 
                amount=amount, 
                account_no=self.account_no, # Added this line
                transaction_type=t_type,
                trans_desc=description
            )
