import django_filters
from .models import Workspace


class CommaSeparatedListFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    def filter(self, qs, value):
        if value:
            values = value.split(',')
            for val in values:
                qs = qs.filter(amenities__icontains=val)
            return qs
        return qs


class WorkspaceFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name="type", lookup_expr='iexact')
    amenities = CommaSeparatedListFilter()
    min_capacity = django_filters.NumberFilter(field_name="capacity", lookup_expr='gte')
    max_capacity = django_filters.NumberFilter(field_name="capacity", lookup_expr='lte')

    class Meta:
        model = Workspace
        fields = ['type', 'amenities', 'min_capacity', 'max_capacity']
