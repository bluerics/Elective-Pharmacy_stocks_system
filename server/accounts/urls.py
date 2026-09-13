
from django.urls import path

from .views import (
    LoginView,
    AccountView,
    ProfileView
)

urlpatterns = [
    path('login/',LoginView.as_view(),name='login'),
    path( '',AccountView.as_view(),name='accounts'),
    path('profile/', ProfileView.as_view(),name='profile'),
]
