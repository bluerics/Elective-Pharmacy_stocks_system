from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer

from stocks.models import Stock


class PurchaseOrderViewSet(viewsets.ModelViewSet):

    queryset = PurchaseOrder.objects.all()

    serializer_class = PurchaseOrderSerializer


    @action(
        detail=True,
        methods=['post']
    )
    def receive(self, request, pk=None):

        purchase_order = self.get_object()

        if purchase_order.stock_received:

            return Response(
                {
                    "message":
                    "This purchase order has already been received."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        if not purchase_order.details.exists():

            return Response(
                {
                    "message":
                    "This purchase order has no order details."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        for detail in purchase_order.details.all():

            stock, created = Stock.objects.get_or_create(

                medicine=detail.medicine,

                supplier=purchase_order.supplier,

                location='Main Storage',

                defaults={
                    'quantity_available':
                    detail.quantity_order
                }
            )

            if not created:

                stock.quantity_available += (
                    detail.quantity_order
                )

                stock.save()

        
        purchase_order.status = 'RECEIVED'

        purchase_order.stock_received = True

        purchase_order.save()

        return Response(
            {
                "message":
                "Purchase order received successfully. Stock updated.",

                "purchase_order_id":
                purchase_order.id,

                "status":
                purchase_order.status
            }
        )