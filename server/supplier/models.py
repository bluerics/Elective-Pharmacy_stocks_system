from django.db import models


class Supplier(models.Model):

    supplier_name = models.CharField(max_length=50)
    supplier_address = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.supplier_name