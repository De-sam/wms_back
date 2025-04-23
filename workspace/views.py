from rest_framework import generics, permissions, filters, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import BaseFilterBackend
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.exceptions import NotFound, ValidationError
from .models import Workspace, Booking
from .filters import WorkspaceFilter, BookingFilter
from .serializers import WorkspaceSerializer, BookingSerializer
from organizations.models import Organization
from rest_framework.views import APIView
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from users.models import ClientUser
from django.db.models import Count
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def check_availability(request):
    workspace_id = request.query_params.get('workspace_id')
    start = parse_datetime(request.query_params.get('start_time'))
    end = parse_datetime(request.query_params.get('end_time'))

    if not all([workspace_id, start, end]):
        return Response({'error': 'Missing parameters'}, status=400)

    conflicts = Booking.objects.filter(
        workspace_id=workspace_id,
        status='ACTIVE',
        workspace__organization__code=request.org_code
    ).filter(
        Q(start_time__lt=end) & Q(end_time__gt=start)
    ).exists()

    return Response({'available': not conflicts})


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Booking.objects.filter(workspace__organization__code=self.request.org_code)
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class WorkspaceCreateView(generics.CreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.organization:
            raise ValidationError("Organization not found in request.")
        serializer.save(organization=self.request.organization)


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class FuzzySearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('search', None)
        if search_query:
            return queryset.annotate(
                similarity=TrigramSimilarity('name', search_query)
            ).filter(similarity__gt=0.2).order_by('-similarity')
        return queryset


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    pagination_class = StandardPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        FuzzySearchFilter,
    ]
    filterset_class = WorkspaceFilter
    ordering_fields = ['name', 'capacity', 'type']

    def perform_create(self, serializer):
        organization = getattr(self.request, 'organization', None)
        if not organization:
            raise ValidationError("Organization could not be determined.")
        serializer.save(organization=organization)

    def get_queryset(self):
        organization = getattr(self.request, 'organization', None)
        if not organization:
            return Workspace.objects.none()
        return Workspace.objects.filter(organization=organization)

class WorkspaceListView(generics.ListAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = WorkspaceFilter
    ordering_fields = ['name', 'type', 'capacity']
    ordering = ['name']

    def get_queryset(self):
        org_code = self.request.org_code
        queryset = Workspace.objects.filter(organization__code=org_code)

        date = self.request.query_params.get('date')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')

        if date or (start_time and end_time):
            if date:
                start = datetime.strptime(date, "%Y-%m-%d")
                end = start + timedelta(days=1)
            else:
                start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

            booked_ids = Booking.objects.filter(
                Q(start_time__lt=end, end_time__gt=start),
                workspace__organization__code=org_code
            ).values_list('workspace_id', flat=True)

            queryset = queryset.exclude(id__in=booked_ids)

        return queryset


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user, workspace__organization__code=self.request.org_code)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user, workspace__organization__code=self.request.org_code)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_queryset(self):
        return Booking.objects.filter(workspace__organization__code=self.request.org_code)

class AdminToggleWorkspaceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, org_code):
        action = request.data.get("action")  # "disable" or "enable"

        if action not in ["disable", "enable"]:
            return Response({"detail": "Invalid action please use 'disable' or 'enable' "}, status=400)

        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found"}, status=404)

        user = request.user
        if not user.is_authenticated or user.organization != organization or not user.is_super_admin:
            return Response({"detail": "Unauthorized"}, status=403)

        if action == "disable":
            # Disable all workspaces
            Workspace.objects.filter(organization=organization).update(status="Unavailable")

            # Cancel all active or upcoming bookings
            Booking.objects.filter(
                workspace__organization=organization,
                status__in=["Booked", "Ongoing"]
            ).update(status="Cancelled", end_time=now())

            return Response({"detail": "All workspaces disabled and bookings cancelled."}, status=200)

        elif action == "enable":
            # Enable all workspaces
            Workspace.objects.filter(organization=organization).update(status="Available")
            return Response({"detail": "All workspaces enabled."}, status=200)

class TopBookedWorkspacesView(APIView):
    def get(self, request):
        top_workspaces = (
            Workspace.objects.annotate(bookings_count=Count('bookings'))
            .order_by('-bookings_count')[:10]
            .values('id', 'name', 'bookings_count')
        )
        return Response(top_workspaces, status=200)

class UpcomingBookingsView(APIView):
    def get(self, request):
        bookings = Booking.objects.filter(
            status="Booked", start_time__gte=now()
        ).order_by('start_time').select_related('workspace', 'user')

        result = [
            {
                "user": b.user.email,
                "workspace": b.workspace.name,
                "start_time": b.start_time,
                "end_time": b.end_time,
                "duration": str(b.end_time - b.start_time)
            }
            for b in bookings
        ]
        return Response(result, status=200)


class RecentActivitiesView(APIView):
    def get(self, request, org_code):
        organization = get_object_or_404(Organization, code=org_code)

        recent_bookings = Booking.objects.filter(
            workspace__organization=organization,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')

        recent_cancellations = Booking.objects.filter(
            workspace__organization=organization,
            status='cancelled',
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-updated_at')

        recent_workspaces = Workspace.objects.filter(
            organization=organization,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')

        completed_sessions = Booking.objects.filter(
            workspace__organization=organization,
            status='completed',
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-updated_at')

        new_users = ClientUser.objects.filter(
            organization=organization,
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).order_by('-date_joined')

        # Analytics: count of bookings per day in past 7 days
        analytics = []
        for i in range(7):
            day = timezone.now().date() - timedelta(days=i)
            count = Booking.objects.filter(
                workspace__organization=organization,
                created_at__date=day
            ).count()
            analytics.append({
                "date": day,
                "count": count
            })

        return Response({
            "recent_bookings": BookingSerializer(recent_bookings, many=True).data,
            "recent_cancellations": BookingSerializer(recent_cancellations, many=True).data,
            "recent_workspaces": WorkspaceSerializer(recent_workspaces, many=True).data,
            "completed_sessions": BookingSerializer(completed_sessions, many=True).data,
            "new_users": ClientUserSerializer(new_users, many=True).data,
            "booking_analytics": analytics
        })
