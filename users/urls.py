from django.urls import path
from .views import ClientUserSignupView

urlpatterns = [
    path('signup/', ClientUserSignupView.as_view(), name='client-user-signup'),
]
# This URL pattern maps the signup endpoint for client users to the ClientUserSignupView.
# The `org_code` parameter is passed to the view to identify the organization.
# The view handles the signup process, including validation and saving the user data.