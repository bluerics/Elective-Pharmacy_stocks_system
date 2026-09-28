from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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

        purchase_order = self.get_object(pk)

        if purchase_order is None:

            return Response(
                {
                    "message":
                    "Purchase order not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )


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
            },
            status=status.HTTP_200_OK
        )