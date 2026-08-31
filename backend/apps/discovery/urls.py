from django.urls import path

from .api import (
    DemoInstructorOnboardingView,
    GeocodingView,
    InstructorSearchView,
    InstructorStateSummaryView,
    PublicProfilePhotoView,
)

urlpatterns = [
    path("instructors/search/", InstructorSearchView.as_view(), name="instructor-search"),
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
]
