from django.db import models

from purchase_orders.models import PurchaseOrder
from medicine.models import Medicine


class PurchaseOrderDetail(models.Model):

    order = models.ForeignKey(PurchaseOrder,on_delete=models.CASCADE,related_name='details')
    medicine = models.ForeignKey(Medicine,on_delete=models.CASCADE,related_name='purchase_order_details')
    quantity_order = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10,decimal_places=2)

    @property
    def subtotal(self):

        return (
            self.quantity_order
            *
            self.unit_cost
        )

    def __str__(self):

        return (
            f"{self.order} - "
            f"{self.medicine.medicine_name}"
        )