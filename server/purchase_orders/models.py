from django.db import models

from supplier.models import Supplier
from accounts.models import Account


class PurchaseOrder(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,related_name='purchase_orders')
    created_by = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True, related_name='purchase_orders')
    order_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='PENDING')
    stock_received = models.BooleanField(default=False)
    def __str__(self):
        return f"PO-{self.id}"