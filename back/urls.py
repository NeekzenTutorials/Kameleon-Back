from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import (
    SignUpView,
    LogInView,
    UserDetailView,
    UserUpdateView,
    SoloRiddleListView,
    CoopRiddleListView,
    RiddleDetailView,
    MemberDetailView,
    MemberRiddlesView,
    MemberCoopRiddlesView,
    IsRiddleSolved,
    IsCoopRiddleSolved,
    GetClue,
    ActivateAccountView,
    MemberDashboardView,
    CreateClanView,
    JoinClanView,
    ClanListView,
    UploadCVView,
    GetCVView,
    RespondCoopInvitationView,
    CoopConnectedMembersView,
    InviteMemberToCoopView,
    FetchReceivedInvitationsView,
    UpdateBioView,
    PasswordResetView,
    PasswordResetConfirmView,
    ClanDetailView,
    RiddleStatsView,
    UpdateRiddleStatsView,
    CheckRiddleStatsView,
    GetRiddleStatsView,
    MemberView,
    UsersWithCVListView,
    GlobalClanStatsView
)

urlpatterns = [
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('activate/<int:user_id>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/login/', LogInView.as_view(), name='login'),
    path('api/user/', UserDetailView.as_view(), name='user-detail'),
    path('api/users/cv/', UsersWithCVListView.as_view(), name='users-with-cv'),
    path('api/members/', MemberDetailView.as_view(), name='member-detail'),
    path('api/members/all/', MemberView.as_view(), name='member-view'),
    path('api/members/update-bio/', UpdateBioView.as_view(), name='update_bio'),
    path('api/members/<str:username>/riddles/', MemberRiddlesView.as_view(), name='member-riddles'),
    path('api/members/<str:username>/riddles/coop/', MemberCoopRiddlesView.as_view(), name='member-coop-riddles'),
    path("api/members/<str:username>/dashboard/", MemberDashboardView.as_view(), name="member_dashboard"),
    path('api/user/update/', UserUpdateView.as_view(), name='user-update'),
    path('api/riddles/', SoloRiddleListView.as_view(), name='riddle-list'),
    path('api/riddles/stats/', RiddleStatsView.as_view(), name='riddle-stats'),
    path('api/riddles/stats/<int:riddle_id>/<str:username>/', GetRiddleStatsView.as_view(), name='get-riddle-stats'),
    path('api/riddles/stats/update/', UpdateRiddleStatsView.as_view(), name='update-riddle-stats'),
    path('api/riddles/stats/check/<int:riddle_id>/<str:member_name>/', CheckRiddleStatsView.as_view(), name='check-riddle-stats'),
    path('api/riddles/coop/', CoopRiddleListView.as_view(), name='riddle-coop-list'),
    path('api/riddles/<int:riddle_id>/', RiddleDetailView.as_view(), name='riddle-detail'),
    path('api/riddles/solve/', IsRiddleSolved.as_view(), name='is-riddle-solved'),
    path('api/riddles/coop/solve/', IsCoopRiddleSolved.as_view(), name='is-coop-riddle-solved'),
    path('api/clans/invite/', InviteMemberToCoopView.as_view(), name='coop-invite'),
    path('api/clans/stats/', GlobalClanStatsView.as_view(), name='global-clan-stats'),
    path('api/clans/invitations/received/', FetchReceivedInvitationsView.as_view(), name='fetch-received-invitations'),
    path('api/coop/invitations/<int:invitation_id>/respond/', RespondCoopInvitationView.as_view(), name='respond-coop-invitation'),
    path('api/coop/members/<int:riddle_id>/', CoopConnectedMembersView.as_view(), name='coop-connected-members'),
    path('api/riddles/clue/', GetClue.as_view(), name='get-clue'),
    path('api/clans/', ClanListView.as_view(), name='clan-list'),
    path('api/clans/create/', CreateClanView.as_view(), name='create-clan'),
    path('api/clans/joinclan/', JoinClanView.as_view(), name='join-clan'),
    path('api/clans/<str:clan_name>/', ClanDetailView.as_view(), name='clan-detail'),
    path('api/cv/upload/', UploadCVView.as_view(), name='upload_cv'),
    path('api/cv/', GetCVView.as_view(), name='get_cv'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
