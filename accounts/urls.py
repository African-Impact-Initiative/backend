from django.urls import path

from .views import ChangeEmailView, GetAdmins, GetUser, UserListCreateAPIView, UserViewUpdateDeleteAPIView, ChangePasswordView, TermsOfUseUpdate, AddOrganizationToUser, PersonInfoUpdate

urlpatterns = [
    path('', UserListCreateAPIView.as_view(), name='user-list'),
    path('me/', GetUser.as_view(), name='user-self'),
    path('admins/', GetAdmins.as_view(), name='admin-users'),
    path('<int:pk>/', UserViewUpdateDeleteAPIView.as_view(), name='user-detail'),
    path('change_password/', ChangePasswordView.as_view(), name='user-password-change'),
    path('change_email/', ChangeEmailView.as_view(), name='user-email-change'),
    path('onboarding/terms', TermsOfUseUpdate.as_view(), name='terms'),
    path('onboarding/personal-info', PersonInfoUpdate.as_view(), name='personal-info'),
    path('onboarding/add-organization', AddOrganizationToUser.as_view(), name='add-organization'),
    # path('activate/<slug:uidb64>/<slug:token>/', activate, name='activate'),
]
