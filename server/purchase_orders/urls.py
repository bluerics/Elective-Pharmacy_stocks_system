from django.urls import path

from .views import PurchaseOrderView
    

urlpatterns = [

    path( '',PurchaseOrderView.as_view(),name='purchase_orders'),
    path('<int:pk>/',PurchaseOrderView.as_view(),name='purchase_orders' ),
    path('<int:pk>/receive/',PurchaseOrderView.as_view(), name='receive_purchase_order' ),

]