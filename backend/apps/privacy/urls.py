from django.urls import path

from .api import PrivacyNoticeView, PrivacyRequestListCreateView

urlpatterns = [
    path("privacy/notice/", PrivacyNoticeView.as_view(), name="privacy-notice"),
    path("privacy/requests/", PrivacyRequestListCreateView.as_view(), name="privacy-requests"),
]
