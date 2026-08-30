from django.urls import path

from .api import (
    DemandAggregateView,
    DemandListCreateView,
    LessonRequestListCreateView,
    LessonRequestTransitionView,
    SessionLoginView,
    SessionLogoutView,
    SessionMeView,
    StudentRegistrationView,
)

urlpatterns = [
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
