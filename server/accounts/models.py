from django.db import models

class Account(models.Model):

    Role_choices =[
        ('ADMIN','Admin'),
        ('STAFF','staff'),
    ]
    username = models.CharField(
        max_length=100,
        unique=True
    )

    password = models.CharField(max_length=255)

    full_name = models.CharField(max_length=150)

    role = models.CharField(
        max_length=20,
        choices=Role_choices,
        default='STAFF'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
