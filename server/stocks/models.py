from django.db import models

from medicine.models import Medicine
from supplier.models import Supplier


class Stock(models.Model):

    medicine = models.ForeignKey(Medicine,on_delete=models.CASCADE, related_name='stocks')
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,related_name='stocks')
    location = models.CharField(max_length=100,default='Main Storage')
    quantity_available = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            'medicine',
            'supplier',
            'location'
        )

    def __str__(self):
        return (
            f"{self.medicine.medicine_name} - "
            f"{self.quantity_available}"
        )
