from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (WorkspaceViewSet,
                    BookingDetailView,
                    BookingCreateView,
                    #AdminToggleWorkspaceView,
                    TopBookedWorkspacesView,
                    UpcomingBookingsView,
                    RecentActivitiesView
                    )

router = DefaultRouter()
#router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('api/', include(router.urls)),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('notification/top-booked-workspaces/', TopBookedWorkspacesView.as_view(), name='top-booked-workspaces'),
    path('notification/upcoming-bookings/', UpcomingBookingsView.as_view(), name='upcoming-bookings'),
    path('notification/recent-activities/', RecentActivitiesView.as_view(), name='recent-activities'),
    #path('notification/workspace/toggle/', AdminToggleWorkspaceView.as_view(), name='toggle-workspaces'),
]
