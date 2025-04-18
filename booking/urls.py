from django.urls import path
from . import views

urlpatterns = [
    # === Super Admin Dashboard ===
    path('admin/dashboard/', views.DashboardSummaryView.as_view(), name='admin-dashboard'),
    path('admin/locations/', views.LocationListCreateView.as_view(), name='location-list-create'),
    path('admin/locations/<int:pk>/', views.LocationRetrieveUpdateDestroyView.as_view(), name='location-detail'),
    path('admin/workspaces/', views.WorkspaceListView.as_view(), name='workspace-list'),
    path('admin/workspaces/<int:pk>/', views.WorkspaceUpdateDestroyView.as_view(), name='workspace-detail'),
    path('admin/bookings/', views.BookingListCreateView.as_view(), name='booking-list-create'),
    path('admin/bookings/<int:pk>/', views.BookingRetrieveUpdateDestroyView.as_view(), name='booking-detail'),

    # === Employee/Learner Dashboard ===
    path('my/bookings/', views.MyBookingsView.as_view(), name='my-bookings'),
    path('my/bookings/history/', views.BookingHistoryView.as_view(), name='booking-history'),
    path('my/bookings/<int:pk>/', views.BookingEditCancelView.as_view(), name='booking-edit-cancel'),
    path('book/', views.CreateBookingView.as_view(), name='create-booking'),
    
    # === General Views ===
    path('available-workspaces/', views.AvailableWorkspacesView.as_view(), name='available-workspaces'),
]
