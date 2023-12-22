from django.urls import path

from .views import OrganizationListCreateAPIView, OrganizationViewUpdateDeleteAPIView, ChallengeUpdate, StageUpdate, FundingUpdate, OrganizationByIdentifierView

urlpatterns = [
    path('', OrganizationListCreateAPIView.as_view(), name='organization-list'),
    path('<int:pk>/', OrganizationViewUpdateDeleteAPIView.as_view(), name='organization-operations'),
    path('challenges/<identifier>/', ChallengeUpdate.as_view(), name='challenge-update'),
    path('funding/<identifier>/', FundingUpdate.as_view(), name='funding-update'),
    path('stages/<identifier>/', StageUpdate.as_view(), name='stage-update'),
    path('identifier/<identifier>/', OrganizationByIdentifierView.as_view(), name='find-by-id'),
]
