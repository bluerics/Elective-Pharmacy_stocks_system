from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import Account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):

        validated_data['password'] = make_password(
            validated_data['password']
        )

        return super().create(validated_data)

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        if password:
            instance.password = make_password(password)

        return super().update(instance, validated_data)