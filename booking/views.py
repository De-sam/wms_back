from rest_framework import viewsets, permissions
from .models import Location, Section, Seat
from .serializers import LocationSerializer, SectionSerializer, SeatSerializer


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or getattr(request.user, 'is_org_super_admin', False))


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return
