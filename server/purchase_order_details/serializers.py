from rest_framework import serializers

from .models import PurchaseOrderDetail


class PurchaseOrderDetailSerializer(
    serializers.ModelSerializer
):

    subtotal = serializers.ReadOnlyField()

    class Meta:

        model = PurchaseOrderDetail

        fields = '__all__'