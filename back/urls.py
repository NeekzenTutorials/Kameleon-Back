from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import (
    SignUpView,
    LogInView,
    UserDetailView,
    UserUpdateView,
    RiddleListView,
    RiddleDetailView,
    MemberDetailView,
    MemberRiddlesView,
    IsRiddleSolved,
    GetClue,
    ActivateAccountView,
    MemberDashboardView,
    CreateClanView,
    JoinClanView
)

urlpatterns = [
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('activate/<int:user_id>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
    path('api/login/', LogInView.as_view(), name='login'),
    path('api/user/', UserDetailView.as_view(), name='user-detail'),
    path('api/member/', MemberDetailView.as_view(), name='member-detail'),
    path('api/members/<str:username>/riddles/', MemberRiddlesView.as_view(), name='member-riddles'),
    path("api/member/<str:username>/dashboard/", MemberDashboardView.as_view(), name="member_dashboard"),
    path('api/user/update/', UserUpdateView.as_view(), name='user-update'),
    path('api/riddles/', RiddleListView.as_view(), name='riddle-list'),
    path('api/riddles/<int:riddle_id>/', RiddleDetailView.as_view(), name='riddle-detail'),
    path('api/riddles/solve/', IsRiddleSolved.as_view(), name='is-riddle-solved'),
    path('api/riddles/clue/', GetClue.as_view(), name='get-clue'),
    path('api/clan/create/', CreateClanView.as_view(), name='create-clan'),
    path('api/clan/join/', JoinClanView.as_view(), name='join-clan'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
