from django.db import models
from django.contrib.auth.models import AbstractUser

class Account(AbstractUser):

    Role_choices =[
        ('ADMIN','Admin'),
        ('STAFF','staff'),
    ]

    full_name = models.CharField(max_length=150)

    role = models.CharField(
        max_length=20,
        choices=Role_choices,
        default='STAFF'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
