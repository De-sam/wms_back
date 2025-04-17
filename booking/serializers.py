from rest_framework import serializers
from .models import (
    Organization, Employee, Location, WorkspaceSection,
    Workspace, Seat, Booking
)

# ======================== BASIC SERIALIZERS =========================

class SeatSerializer(serializers.ModelSerializer):
    qr_uuid = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Seat
        fields = ['uuid', 'identifier', 'qr_uuid']

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'org_code']


class WorkspaceSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'type', 'capacity', 'description',
            'amenities', 'is_available', 'seats', 'amenities'
        ]



class WorkspaceSectionSerializer(serializers.ModelSerializer):
    workspaces = WorkspaceSerializer(many=True, read_only=True)

    class Meta:
        model = WorkspaceSection
        fields = ['id', 'name', 'capacity', 'workspaces']


class LocationSerializer(serializers.ModelSerializer):
    sections = WorkspaceSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'city', 'state', 'address',
            'total_capacity', 'sections'
        ]

# ======================== CREATE SERIALIZERS =========================

class SeatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['identifier']


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    seats = SeatCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Workspace
        fields = [
            'name', 'type', 'capacity', 'description',
            'amenities', 'is_available', 'seats'
        ]

    def create(self, validated_data):
        seats_data = validated_data.pop('seats')
        workspace = Workspace.objects.create(**validated_data)
        for seat_data in seats_data:
            Seat.objects.create(workspace=workspace, label=seat_data['label'])
        return workspace


class WorkspaceSectionCreateSerializer(serializers.ModelSerializer):
    workspaces = WorkspaceCreateSerializer(many=True, write_only=True)

    class Meta:
        model = WorkspaceSection
        fields = ['name', 'capacity', 'workspaces']

    def create(self, validated_data):
        workspaces_data = validated_data.pop('workspaces')
        section = WorkspaceSection.objects.create(**validated_data)

        for workspace_data in workspaces_data:
            seats_data = workspace_data.pop('seats')
            workspace = Workspace.objects.create(section=section, **workspace_data)
            for seat in seats_data:
                Seat.objects.create(workspace=workspace, label=seat['label'])

        return section


class LocationCreateSerializer(serializers.ModelSerializer):
    sections = WorkspaceSectionCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Location
        fields = ['name', 'city', 'state', 'address', 'total_capacity', 'sections']

    def validate(self, attrs):
        request = self.context['request']
        if not request.user.is_authenticated or request.user.role != 'Admin':
            raise serializers.ValidationError("Only super admins can create locations.")
        return attrs

    def create(self, validated_data):
        sections_data = validated_data.pop('sections')
        user = self.context['request'].user
        organization = user.organization

        location = Location.objects.create(organization=organization, **validated_data)

        for section_data in sections_data:
            workspaces_data = section_data.pop('workspaces')
            section = WorkspaceSection.objects.create(location=location, **section_data)

            for workspace_data in workspaces_data:
                seats_data = workspace_data.pop('seats')
                workspace = Workspace.objects.create(section=section, **workspace_data)
                for seat in seats_data:
                    Seat.objects.create(workspace=workspace, label=seat['label'])

        return location

# ======================== BOOKING SERIALIZER =========================

class BookingSerializer(serializers.ModelSerializer):
    seat = SeatSerializer(read_only=True)
    seat_id = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(), source="seat", write_only=True
    )

    class Meta:
        model = Booking
        fields = ['id', 'seat', 'seat_id', 'start_time', 'end_time', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        return Booking.objects.create(user=user, **validated_data)
