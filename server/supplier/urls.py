from django.urls import path

from .views import SupplierView


urlpatterns = [

    path('',SupplierView.as_view(),name='suppliers'),
    path('<int:pk>/',SupplierView.as_view(), name='supplier'),

]