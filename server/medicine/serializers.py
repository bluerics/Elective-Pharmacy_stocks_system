from rest_framework import serializers

from .models import Medicine


class MedicineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicine
        fields = '__all__'

    def validate_medicine_type (self, value):
        return value.strip().upper()