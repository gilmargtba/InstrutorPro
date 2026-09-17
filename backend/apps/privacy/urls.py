from django.urls import path

from .api import (
    LegalAcceptanceListCreateView,
    LegalDocumentView,
    PrivacyNoticeView,
    PrivacyRequestListCreateView,
)

urlpatterns = [
    path("privacy/notice/", PrivacyNoticeView.as_view(), name="privacy-notice"),
    path("privacy/requests/", PrivacyRequestListCreateView.as_view(), name="privacy-requests"),
    path("legal/documents/<str:audience>/", LegalDocumentView.as_view(), name="legal-document"),
    path("legal/acceptances/", LegalAcceptanceListCreateView.as_view(), name="legal-acceptances"),
]
