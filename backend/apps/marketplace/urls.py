from django.conf import settings
from django.urls import path

from .api import (
    DemandAggregateView,
    DemandListCreateView,
    InstructorAdvancedAnalyticsView,
    InstructorDocumentDownloadView,
    InstructorSaaSSummaryView,
    LessonRequestListCreateView,
    LessonRequestTransitionView,
    ProfilePhotoPrivateDownloadView,
    SessionLoginView,
    SessionLogoutView,
    SessionMeView,
    StudentRegistrationView,
)

urlpatterns = [
    path("marketplace/instructor/saas-summary/", InstructorSaaSSummaryView.as_view()),
    path("marketplace/instructor/advanced-analytics/", InstructorAdvancedAnalyticsView.as_view()),
    path("marketplace/session/login/", SessionLoginView.as_view()),
    path("marketplace/session/logout/", SessionLogoutView.as_view()),
    path("marketplace/session/me/", SessionMeView.as_view()),
    path(
        "marketplace/profile-photos/<uuid:pk>/download/",
        ProfilePhotoPrivateDownloadView.as_view(),
        name="profile-photo-private-download",
    ),
    path(
        "marketplace/instructor-documents/<uuid:pk>/download/",
        InstructorDocumentDownloadView.as_view(),
        name="instructor-document-download",
    ),
]

if settings.APP_ENV != "PRODUCTION":
    urlpatterns += [
        path("demo/marketplace/students/register/", StudentRegistrationView.as_view()),
        path("demo/marketplace/session/logout/", SessionLogoutView.as_view()),
        path("demo/marketplace/session/login/", SessionLoginView.as_view()),
        path("demo/marketplace/session/me/", SessionMeView.as_view()),
        path("demo/marketplace/demands/", DemandListCreateView.as_view()),
        path("demo/marketplace/demand-aggregates/", DemandAggregateView.as_view()),
        path("demo/marketplace/lesson-requests/", LessonRequestListCreateView.as_view()),
        path(
            "demo/marketplace/lesson-requests/<uuid:pk>/transition/",
            LessonRequestTransitionView.as_view(),
        ),
    ]
