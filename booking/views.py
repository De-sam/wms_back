from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import (
    Location, WorkspaceSection, Workspace,
    Seat, Booking, Employee
)
from .serializers import (
    LocationSerializer, LocationCreateSerializer,
    WorkspaceSerializer, BookingSerializer
)
from datetime import date

# ================= SUPER ADMIN VIEWS =================

class DashboardSummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'Admin':
            return Response({'detail': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)

        organization = user.organization
        total_workspaces = Workspace.objects.filter(section__location__organization=organization).count()
        total_users = Employee.objects.filter(organization=organization).count()
        today = date.today()
        bookings_today = Booking.objects.filter(
            seat__workspace__section__location__organization=organization,
            start_time__date=today
        ).count()
        total_seats = Seat.objects.filter(workspace__section__location__organization=organization).count()
        occupied_seats = Booking.objects.filter(
            seat__workspace__section__location__organization=organization,
            start_time__date=today
        ).count()
        occupancy_rate = int((occupied_seats / total_seats) * 100) if total_seats else 0

        return Response({
            "total_workspaces": total_workspaces,
            "total_users": total_users,
            "bookings_today": bookings_today,
            "occupancy_rate": occupancy_rate
        })


class LocationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Location.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LocationCreateSerializer
        return LocationSerializer

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)


# ================= EMPLOYEE/LEARNER VIEWS =================

class MyBookingsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class CreateBookingView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingSerializer


# ================= GENERAL VIEWS =================

class AvailableWorkspacesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        queryset = Workspace.objects.filter(is_available=True)
        type_filter = self.request.query_params.get('type')
        capacity_filter = self.request.query_params.get('capacity')

        if type_filter:
            queryset = queryset.filter(type=type_filter)
        if capacity_filter:
            queryset = queryset.filter(capacity__gte=capacity_filter)

        return queryset.distinct()
