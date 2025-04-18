from django_filters import rest_framework as filters
from .models import Workspace, Booking, Location

class WorkspaceFilter(filters.FilterSet):
    amenities = filters.CharFilter(method='filter_amenities')
    location = filters.CharFilter(field_name='section__location__name', lookup_expr='icontains')

    class Meta:
        model = Workspace
        fields = ['type', 'is_available']

    def filter_amenities(self, queryset, name, value):
        amenities = value.split(',')
        for amenity in amenities:
            queryset = queryset.filter(amenities__icontains=amenity.strip())
        return queryset


class BookingFilter(filters.FilterSet):
    date = filters.DateFilter(field_name='start_time', lookup_expr='date')
    start_after = filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    end_before = filters.DateTimeFilter(field_name='end_time', lookup_expr='lte')

    class Meta:
        model = Booking
        fields = ['seat__workspace__section__location__name']

class BookingHistoryFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="start_time", lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="end_time", lookup_expr='lte')

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
    