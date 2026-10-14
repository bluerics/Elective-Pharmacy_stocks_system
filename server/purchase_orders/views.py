from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer

from stocks.models import Stock


class PurchaseOrderView(APIView):

    def get_object(self, pk):

        try:

            return PurchaseOrder.objects.get(pk=pk)

        except PurchaseOrder.DoesNotExist:

            return None


    def get(self, request, pk=None):

        if pk is not None:

            purchase_order = self.get_object(pk)

            if purchase_order is None:

                return Response(
                    {
                        "message":
                        "Purchase order not found."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PurchaseOrderSerializer(
                purchase_order
            )

            return Response(serializer.data)


        purchase_orders = PurchaseOrder.objects.all()

        serializer = PurchaseOrderSerializer(
            purchase_orders,
            many=True
        )

        return Response(serializer.data)


    def post(self, request):

        serializer = PurchaseOrderSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def put(self, request, pk):

        purchase_order = self.get_object(pk)

        if purchase_order is None:

            return Response(
                {
                    "message":
                    "Purchase order not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseOrderSerializer(
            purchase_order,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def patch(self, request, pk):

        purchase_order = self.get_object(pk)

        if purchase_order is None:

            return Response(
                {
                    "message":
                    "Purchase order not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseOrderSerializer(
            purchase_order,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def delete(self, request, pk):

        purchase_order = self.get_object(pk)

        if purchase_order is None:

            return Response(
                {
                    "message":
                    "Purchase order not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        purchase_order.delete()

        return Response(
            {
                "message":
                "Purchase order deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )


    
    def receive(self, request, pk):
        try:
            with transaction.atomic():

                # Lock the purchase order to prevent duplicate receiving.
                try:
                    purchase_order = (
                        PurchaseOrder.objects
                        .select_for_update()
                        .get(pk=pk)
                    )
                except PurchaseOrder.DoesNotExist:
                    return Response(
                        {"message": "Purchase order not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Prevent receiving the same order twice.
                if purchase_order.stock_received:
                    return Response(
                        {
                            "message":
                            "This purchase order has already been received."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Cancelled orders cannot be received.
                if purchase_order.status == "CANCELLED":
                    return Response(
                        {
                            "message":
                            "Cancelled purchase orders cannot be received."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Retrieve the order details.
                details = list(purchase_order.details.all())

                if not details:
                    return Response(
                        {
                            "message":
                            "This purchase order has no order details."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Add ordered quantities to inventory.
                for detail in details:

                    stock, created = Stock.objects.get_or_create(
                        medicine=detail.medicine,
                        supplier=purchase_order.supplier,
                        location="Main Storage",
                        defaults={
                            "quantity_available": detail.quantity_order
                        }
                    )

                    if not created:
                        # Lock the existing stock row before updating it.
                        stock = Stock.objects.select_for_update().get(
                            pk=stock.pk
                        )

                        stock.quantity_available += detail.quantity_order

                        stock.save(
                            update_fields=["quantity_available"]
                        )

                # Mark the purchase order as received.
                purchase_order.status = "RECEIVED"
                purchase_order.stock_received = True

                purchase_order.save(
                    update_fields=["status", "stock_received"]
                )

                return Response(
                    {
                        "message":
                        "Purchase order received successfully. Stock updated.",
                        "purchase_order_id": purchase_order.id,
                        "status": purchase_order.status,
                        "stock_received": purchase_order.stock_received
                    },
                    status=status.HTTP_200_OK
                )

        except Exception:
            return Response(
                {
                    "message":
                    "Failed to receive purchase order. No partial changes were saved."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReceivePurchaseOrderView(PurchaseOrderView):

    def post(self, request, pk):
        return self.receive(request, pk)
