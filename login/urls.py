from django.urls import path
from .views import LoginView

app_name = "login"

urlpatterns = [
    path('login/', LoginView.as_view(), name='organization-login'),
]
