from django.urls import path
from .views import SignUpView, LogInView

urlpatterns = [
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('api/login/', LogInView.as_view(), name='login'),
]
