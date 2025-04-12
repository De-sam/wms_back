from django.urls import path, include

urlpatterns = [
    path("login/", include("users.org_urls")),         # users/views/login tied to org
    path("bookings/", include("booking.org_urls")),    # bookings tied to org
]