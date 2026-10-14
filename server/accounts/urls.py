
from django.urls import path

from .views import (
    LoginView,
    AccountView,
    ProfileView
)

urlpatterns = [
    path('login/',LoginView.as_view(),name='login'),
    path('profile/', ProfileView.as_view(),name='profile'),
    path( '',AccountView.as_view(),name='accounts'),
    path('<int:pk>/', AccountView.as_view(), name='account_detail'),
]
