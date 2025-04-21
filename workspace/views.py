from rest_framework import generics, permissions, filters, viewsets
from .models import Section, Workspace, Booking
from django.db.models import Q
from django.utils import timezone
from .filters import WorkspaceFilter
from datetime import datetime, timedelta
import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.filters import BaseFilterBackend
from .serializers import SectionSerializer, WorkspaceSerializer, BookingSerializer


class SectionCreateView(generics.CreateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class SectionListView(generics.ListAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingListView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
