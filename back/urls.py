from django.urls import path
from .views import SignUpView

urlpatterns = [
    path('api/signup/', SignUpView.as_view(), name='signup'),
]
