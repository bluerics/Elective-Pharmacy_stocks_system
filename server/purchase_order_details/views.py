from decimal import Decimal

from rest_framework import viewsets

from .models import PurchaseOrderDetail
from .serializers import PurchaseOrderDetailSerializer


class PurchaseOrderDetailViewSet(viewsets.ModelViewSet):

    queryset = PurchaseOrderDetail.objects.all()

    serializer_class = PurchaseOrderDetailSerializer


    def update_purchase_order_total(self, order):

        total = Decimal('0.00')

        for detail in order.details.all():

            total += (detail.quantity_order*detail.unit_cost)

        order.total_amount = total

        order.save()


    def perform_create(self, serializer):

        detail = serializer.save()

        self.update_purchase_order_total(detail.order)


    def perform_update(self, serializer):

        old_order = self.get_object().order

        detail = serializer.save()


        self.update_purchase_order_total(detail.order)

        if old_order != detail.order:

            self.update_purchase_order_total(old_order)


    def perform_destroy(self, instance):

        order = instance.order

        instance.delete()

        self.update_purchase_order_total(order)