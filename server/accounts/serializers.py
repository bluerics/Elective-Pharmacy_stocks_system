
from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = [
            'id',
            'username',
            'password',
            'full_name',
            'role',
            'created_at',
        ]

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):

        password = validated_data.pop('password')

        account = Account(**validated_data)

        account.set_password(password)

        account.save()

        return account
