from django.urls import path

from .api import PaymentWebhookView

urlpatterns = [path("payments/webhook/<str:provider>/", PaymentWebhookView.as_view())]
