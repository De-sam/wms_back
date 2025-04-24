from django.urls import path
from .views import ClientUserSignupView, ToggleNotificationView, GetNotificationStatusView, OrganizationUsersView, ApproveOrDeclineUserView

urlpatterns = [
    path('signup/', ClientUserSignupView.as_view(), name='client-user-signup'),
    path('toggle-notifications/', ToggleNotificationView.as_view(), name='toggle-notifications'),
    path('notification-status/', GetNotificationStatusView.as_view(), name='get-notification-status'),
    path('', OrganizationUsersView.as_view(), name='organization-users'),
    path('approve-decline/', ApproveOrDeclineUserView.as_view(), name='approve-decline-user'),
]
# This URL pattern maps the signup endpoint for client users to the ClientUserSignupView.
# The `org_code` parameter is passed to the view to identify the organization.
# The view handles the signup process, including validation and saving the user data.