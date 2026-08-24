from django.urls import path

from .api import DemoInstructorOnboardingView, GeocodingView, InstructorSearchView

urlpatterns = [
    path("instructors/search/", InstructorSearchView.as_view(), name="instructor-search"),
    path("geocoding/search/", GeocodingView.as_view(), name="geocoding-search"),
    path(
        "demo/instructor-onboarding/",
        DemoInstructorOnboardingView.as_view(),
        name="demo-instructor-onboarding",
    ),
]
