from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PurchaseOrderDetailViewSet


router = DefaultRouter()

router.register(
    r'purchase-order-details',
    PurchaseOrderDetailViewSet
)


urlpatterns = [
    path('', include(router.urls)),
]