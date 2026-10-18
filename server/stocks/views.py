from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Stock
from .serializers import StockSerializer
from rest_framework.permissions import IsAuthenticated


class StockView(APIView):
    permission_classes=[IsAuthenticated]

    def get_object(self, pk):

        try:

            return Stock.objects.get(pk=pk)

        except Stock.DoesNotExist:

            return None


    def get(self, request, pk=None):

        # Get one stock
        if pk is not None:

            stock = self.get_object(pk)

            if stock is None:

                return Response(
                    {
                        "message":
                        "Stock not found."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = StockSerializer(stock)

            return Response(serializer.data)


        # Get low stocks
        if request.path.endswith('/low-stock/'):

            low_stocks = []

            stocks = Stock.objects.select_related(
                'medicine'
            )

            for stock in stocks:

                if (
                    stock.quantity_available
                    <= stock.medicine.reorder_level
                ):

                    low_stocks.append(stock)

            serializer = StockSerializer(
                low_stocks,
                many=True
            )

            return Response(serializer.data)


        # Get all stocks
        stocks = Stock.objects.all()

        serializer = StockSerializer(
            stocks,
            many=True
        )

        return Response(serializer.data)


    def post(self, request):

        serializer = StockSerializer(
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

        stock = self.get_object(pk)

        if stock is None:

            return Response(
                {
                    "message":
                    "Stock not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StockSerializer(
            stock,
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

        stock = self.get_object(pk)

        if stock is None:

            return Response(
                {
                    "message":
                    "Stock not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StockSerializer(
            stock,
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
        if request.user.role !="ADMIN":
            return Response(
                {
                    "message": "Only Admin can delete stock."
                
                },
                status=status.HTTP_403_FORBIDDEN
            )

        stock = self.get_object(pk)

        if stock is None:

            return Response(
                {
                    "message":
                    "Stock not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        stock.delete()

        return Response(
            {
                "message":
                "Stock deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )