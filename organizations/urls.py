from django.urls import path

from .views import OrganizationListCreateAPIView, OrganizationViewUpdateDeleteAPIView, ChallengeUpdate, StageUpdate, FundingUpdate, OrganizationByIdentifierView, UploadLogo, OrganizationMembersView, UpdateOrganizationMemberView, UpdateMemberCoownerStatusView, JoinRequestViewSet

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
    
    path('join-requests/', JoinRequestViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='join-request-list'),
    path('join-requests/<int:pk>/', JoinRequestViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='join-request-detail'),
    path('join-requests/<int:pk>/accept/', 
        JoinRequestViewSet.as_view({'post': 'accept'}),
        name='accept-join-request'),
    path('join-requests/<int:pk>/decline/', 
        JoinRequestViewSet.as_view({'post': 'decline'}),
        name='decline-join-request'),
    path('join-requests/current/', 
        JoinRequestViewSet.as_view({'get': 'current'}),
        name='current-join-request'),
]
