from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, BookingDetailView

router = DefaultRouter()
#router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('api/', include(router.urls)),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
]
