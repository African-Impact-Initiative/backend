from django.urls import path

from .views import OrganizationListCreateAPIView, OrganizationViewUpdateDeleteAPIView, ChallengeUpdate, StageUpdate, FundingUpdate, OrganizationByIdentifierView, UploadLogo, OrganizationMembersView, UpdateOrganizationMemberView, UpdateMemberCoownerStatusView

urlpatterns = [
    path('', OrganizationListCreateAPIView.as_view(), name='organization-list'),
    path('<int:pk>/', OrganizationViewUpdateDeleteAPIView.as_view(), name='organization-operations'),
    path('challenges/<identifier>/', ChallengeUpdate.as_view(), name='challenge-update'),
    path('funding/<identifier>/', FundingUpdate.as_view(), name='funding-update'),
    path('stages/<identifier>/', StageUpdate.as_view(), name='stage-update'),
    path('identifier/<identifier>/', OrganizationByIdentifierView.as_view(), name='find-by-id'),
    path('upload-logo/<int:pk>/', UploadLogo.as_view(), name='upload-logo'),
    path('members/<int:organization_id>/', OrganizationMembersView.as_view(), name='organization-members'),
    path('members/<int:organization_id>/user/<int:user_id>/', UpdateOrganizationMemberView.as_view(), name='update-organization-member'),
    path('members/<int:organization_id>/user/<int:user_id>/coowner/', 
     UpdateMemberCoownerStatusView.as_view(), 
     name='update-member-coowner-status'),
]
