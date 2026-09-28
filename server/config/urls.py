from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),
    path('api/medicines/', include('medicine.urls')),
    path('api/supplier/', include('supplier.urls')),
    path('api/stocks/', include('stocks.urls')),
    path('api/purchase_orders/', include('purchase_orders.urls')),
    path('api/purchase_order_details/', include('purchase_order_details.urls')),
]