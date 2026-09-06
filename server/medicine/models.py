from django.db import models


class Medicine(models.Model):

    MEDICINE_TYPE_CHOICES = [
        ('PRESCRIPTION', 'Prescription'),
        ('OTC', 'OTC'),
    ]

    medicine_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100,blank=True,null=True)
    category = models.CharField(max_length=100)
    dosage_form = models.CharField(max_length=100)
    strength = models.CharField(max_length=100)
    reorder_level = models.IntegerField(default=10)
    medicine_type = models.CharField(max_length=20,choices=MEDICINE_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=100)
    expiry_date = models.DateField()

    def __str__(self):
        return self.medicine_name