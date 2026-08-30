from django.urls import path

from .api import (
    DemandAggregateView,
    DemandListCreateView,
    LessonRequestListCreateView,
    LessonRequestTransitionView,
    SessionLogoutView,
    StudentRegistrationView,
)

urlpatterns = [
    path("demo/marketplace/students/register/", StudentRegistrationView.as_view()),
    path("demo/marketplace/session/logout/", SessionLogoutView.as_view()),
    path("demo/marketplace/demands/", DemandListCreateView.as_view()),
    path("demo/marketplace/demand-aggregates/", DemandAggregateView.as_view()),
    path("demo/marketplace/lesson-requests/", LessonRequestListCreateView.as_view()),
    path(
        "demo/marketplace/lesson-requests/<uuid:pk>/transition/",
        LessonRequestTransitionView.as_view(),
    ),
]
