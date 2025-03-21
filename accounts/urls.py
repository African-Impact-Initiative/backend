
from django.urls import path, include

from .views import ChangeEmailView, GetAdmins, GetUser, UserListCreateAPIView, UserViewUpdateDeleteAPIView, ChangePasswordView, TermsOfUseUpdate, AddOrganizationToUser, PersonInfoUpdate, UpdateTeamStatus, InvitationViewSet, ProcessInvitationView, activate, GoogleView
print(GoogleView)
urlpatterns = [
    path('', UserListCreateAPIView.as_view(), name='user-list'),
    path('me/', GetUser.as_view(), name='user-self'),
    path('admins/', GetAdmins.as_view(), name='admin-users'),
    path('<int:pk>/', UserViewUpdateDeleteAPIView.as_view(), name='user-detail'),
    path('change_password/', ChangePasswordView.as_view(), name='user-password-change'),
    path('change_email/', ChangeEmailView.as_view(), name='user-email-change'),
    path('onboarding/terms/', TermsOfUseUpdate.as_view(), name='terms'),
    path('onboarding/personal-info/', PersonInfoUpdate.as_view(), name='personal-info'),
    path('onboarding/add-organization/', AddOrganizationToUser.as_view(), name='add-organization'),
    path('activate/', activate, name='activate'),
    path('users/team-status/', UpdateTeamStatus.as_view(), name='update-team-status'),
    # path('activate/<slug:uidb64>/<slug:token>/', activate, name='activate'),
    # Invitation URLs
    path('invitations/', InvitationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='invitation-list'),
    
    # URL for processing invitations using token
    path('invitations/process/<str:token>/', 
         ProcessInvitationView.as_view(), 
         name='process-invitation'),
    path('invitations/<int:pk>/', InvitationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('invitations/<int:pk>/accept/', InvitationViewSet.as_view({'post': 'accept'})),
    path('invitations/<int:pk>/decline/', InvitationViewSet.as_view({'post': 'decline'})),
    path('invitations/<int:pk>/withdraw/', InvitationViewSet.as_view({'post': 'withdraw'})),
    path('invitations/<int:pk>/resend/', InvitationViewSet.as_view({'post': 'resend'})),
    path('activate/<slug:uidb64>/<slug:token>/', activate, name='activate'),
    path('auth/google/login/', GoogleView, name='google-login'),
    path('auth/google/', include('social_django.urls', namespace='social')),  # Google OAuth
]
