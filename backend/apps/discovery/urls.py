from django.urls import path

from .api import (
    DemoInstructorOnboardingDraftView,
    DemoInstructorOnboardingSubmitView,
    DemoInstructorOnboardingView,
    GeocodingView,
    InstructorSearchView,
    InstructorStateSummaryView,
    PublicInstructorProfileView,
    PublicProfilePhotoView,
    WhatsAppContactView,
)

urlpatterns = [
    path("instructors/search/", InstructorSearchView.as_view(), name="instructor-search"),
    path(
        "instructors/<uuid:pk>/", PublicInstructorProfileView.as_view(), name="instructor-profile"
    ),
    path(
        "instructors/<uuid:pk>/whatsapp-contact/",
        WhatsAppContactView.as_view(),
        name="instructor-whatsapp-contact",
    ),
    path("instructors/states/", InstructorStateSummaryView.as_view(), name="instructor-states"),
    path(
        "instructors/profile-photos/<uuid:pk>/",
        PublicProfilePhotoView.as_view(),
        name="public-profile-photo",
    ),
    path("geocoding/search/", GeocodingView.as_view(), name="geocoding-search"),
    path(
        "demo/instructor-onboarding/",
        DemoInstructorOnboardingView.as_view(),
        name="demo-instructor-onboarding",
    ),
    path(
        "demo/instructor-onboarding/draft/",
        DemoInstructorOnboardingDraftView.as_view(),
        name="demo-instructor-onboarding-draft",
    ),
    path(
        "demo/instructor-onboarding/submit/",
        DemoInstructorOnboardingSubmitView.as_view(),
        name="demo-instructor-onboarding-submit",
    ),
]
