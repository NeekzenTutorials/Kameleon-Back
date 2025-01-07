from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import SignUpView, LogInView, UserDetailView, UserUpdateView, RiddleListView, RiddleDetailView, MemberDetailView

urlpatterns = [
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('api/login/', LogInView.as_view(), name='login'),
    path('api/user/', UserDetailView.as_view(), name='user-detail'),
    path('api/member/', MemberDetailView.as_view(), name='member-detail'),
    path('api/user/update/', UserUpdateView.as_view(), name='user-update'),
    path('api/riddles/', RiddleListView.as_view(), name='riddle-list'),
    path('api/riddles/<int:riddle_id>/', RiddleDetailView.as_view(), name='riddle-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
