from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Stock
from .serializers import StockSerializer


class StockViewSet(viewsets.ModelViewSet):

    queryset = Stock.objects.all()

    serializer_class = StockSerializer


    @action(
        detail=False,
        methods=['get']
    )
    def low_stock(self, request):

        low_stocks = []

        stocks = Stock.objects.select_related('medicine')

        for stock in stocks:

            if (stock.quantity_available <= stock.medicine.reorder_level):

                low_stocks.append(stock)

        serializer = self.get_serializer(low_stocks,many=True)

        return Response(serializer.data)