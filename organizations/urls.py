from django.urls import path
from .views import (
    OrganizationSignupView,
    ActivateOrganizationView,
    ResendActivationTokenView,  # ✅ import it
)

urlpatterns = [
    path('signup/', OrganizationSignupView.as_view(), name='organization-signup'),
    path('activate/<uuid:token>/', ActivateOrganizationView.as_view(), name='organization-activate'),
    path('resend-activation/', ResendActivationTokenView.as_view(), name='resend-activation'),  # ✅ new endpoint
]
