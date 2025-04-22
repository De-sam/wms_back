from rest_framework import generics, permissions, filters, viewsets
from .models import Workspace, Booking
from django.db.models import Q
from django.utils import timezone
from .filters import WorkspaceFilter, BookingFilter
from datetime import datetime, timedelta
import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.filters import BaseFilterBackend
from .serializers import WorkspaceSerializer, BookingSerializer
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_datetime

@api_view(['GET'])
def check_availability(request):
    workspace_id = request.query_params.get('workspace_id')
    start = parse_datetime(request.query_params.get('start_time'))
    end = parse_datetime(request.query_params.get('end_time'))

    if not all([workspace_id, start, end]):
        return Response({'error': 'Missing parameters'}, status=400)

    conflicts = Booking.objects.filter(
        workspace_id=workspace_id,
        status='ACTIVE',  # only active bookings count as conflicts
    ).filter(
        Q(start_time__lt=end) & Q(end_time__gt=start)
    ).exists()

    return Response({'available': not conflicts})

class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optional: limit non-admins to only their bookings
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

class WorkspaceCreateView(generics.CreateAPIView):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    pagination_class = StandardPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        FuzzySearchFilter,
    ]
    filterset_class = WorkspaceFilter
    ordering_fields = ['name', 'capacity', 'type']

class WorkspaceListView(generics.ListAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = WorkspaceFilter
    ordering_fields = ['name', 'type', 'capacity']
    ordering = ['name']  # default ordering

    def get_queryset(self):
        queryset = Workspace.objects.all()
        date = self.request.query_params.get('date')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')

        # Filter by availability on a specific date or time range
        if date or (start_time and end_time):
            if date:
                start = datetime.strptime(date, "%Y-%m-%d")
                end = start + timedelta(days=1)
            else:
                start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

            booked_ids = Booking.objects.filter(
                Q(start_time__lt=end, end_time__gt=start)
            ).values_list('workspace_id', flat=True)

            queryset = queryset.exclude(id__in=booked_ids)

        return queryset


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()  # or Booking.objects.all() if you prefer
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingListView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

