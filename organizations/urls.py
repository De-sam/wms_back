from django.urls import path
from .views import OrganizationSignupView, ActivateOrganizationView

urlpatterns = [
    path('signup/', OrganizationSignupView.as_view(), name='organization-signup'),
    path('activate/<uuid:token>/', ActivateOrganizationView.as_view(), name='organization-activate'),
]
