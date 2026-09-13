from rest_framework import serializers

from .models import Stock


class StockSerializer(serializers.ModelSerializer):

    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True )
    supplier_name = serializers.CharField(source='supplier.supplier_name',read_only=True)

    class Meta:

        model = Stock

        fields = [
            'id',
            'medicine',
            'medicine_name',
            'supplier',
            'supplier_name',
            'location',
            'quantity_available',
            'last_updated'
        ]