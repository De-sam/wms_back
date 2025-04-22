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
from rest_framework.exceptions import NotFound
from .models import Workspace, Booking
from .filters import WorkspaceFilter, BookingFilter
from .serializers import WorkspaceSerializer, BookingSerializer
from organizations.models import Organization


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
        try:
            org = Organization.objects.get(code=self.request.org_code)
        except Organization.DoesNotExist:
            raise NotFound("Invalid organization code.")
        
        serializer.save(organization=org)


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

    def get_queryset(self):
        return Workspace.objects.filter(organization__code=self.request.org_code)


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
