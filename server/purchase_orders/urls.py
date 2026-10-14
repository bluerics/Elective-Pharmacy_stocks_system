from django.urls import path

from .views import (
    PurchaseOrderView,
    ReceivePurchaseOrderView,
)

urlpatterns = [
    path(
        "",
        PurchaseOrderView.as_view(),
        name="purchase_order_list"
    ),

    path(
        "<int:pk>/",
        PurchaseOrderView.as_view(),
        name="purchase_order_detail"
    ),

    path(
        "<int:pk>/receive/",
        ReceivePurchaseOrderView.as_view(),
        name="purchase_order_receive"
    ),
]
