from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/', include('accounts.urls')),
    path('api/', include('medicine.urls')),
    path('api/', include('supplier.urls')),
    path('api/', include('stocks.urls')),
    path('api/', include('purchase_orders.urls')),
    path('api/', include('purchase_order_details.urls')),
]