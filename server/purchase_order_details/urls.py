from django.urls import path

from .views import PurchaseOrderDetailView
  



urlpatterns = [

    path( '',PurchaseOrderDetailView.as_view(), name='purchase_order_details'),
    path('<int:pk>/',PurchaseOrderDetailView.as_view(),name='purchase_order_detail' ),

]