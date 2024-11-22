from django.urls import path
from . import views

urlpatterns = [
    path('latest-users/', views.latest_users, name='latest_users'),
]
