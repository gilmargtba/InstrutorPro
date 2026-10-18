from django.urls import path

from .cfc_api import (
    CFCDetailView,
    CFCInstructorActivationView,
    CFCInstructorListCreateView,
    CFCInstructorResendView,
    CFCMembershipListView,
)

urlpatterns = [
    path("cfc/memberships/", CFCMembershipListView.as_view()),
    path("cfc/<uuid:cfc_id>/", CFCDetailView.as_view()),
    path("cfc/<uuid:cfc_id>/instructors/", CFCInstructorListCreateView.as_view()),
    path(
        "cfc/<uuid:cfc_id>/instructors/<uuid:link_id>/resend/",
        CFCInstructorResendView.as_view(),
    ),
    path("cfc/activate-instructor/", CFCInstructorActivationView.as_view()),
]
