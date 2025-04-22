from django.urls import path
from .views import LoginView, AdminLoginView, CombinedLoginView

app_name = "login"

urlpatterns = [
    path('login/', LoginView.as_view(), name='organization-login'),
    #path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/login/', CombinedLoginView.as_view(), name='admin-login'),
]
