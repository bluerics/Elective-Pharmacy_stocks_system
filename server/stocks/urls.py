from django.urls import path

from .views import StockView
    


urlpatterns = [

    path('',StockView.as_view(),name='stocks'),
    path('<int:pk>/',StockView.as_view(),  name='stock'),
    path('low-stock/',StockView.as_view(),name='low_stock'),

]