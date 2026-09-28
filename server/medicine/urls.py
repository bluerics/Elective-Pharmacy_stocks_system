from django.urls import path

from .views import MedicineView


urlpatterns = [

    path('', MedicineView.as_view(),name='medicines'),
    path('<int:pk>/', MedicineView.as_view(), name='medicine' ),

]