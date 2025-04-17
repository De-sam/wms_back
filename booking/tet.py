from rest_framework import serializers
from .models import (
    Organization, Location, Section,
    Workspace, Seat, Booking
)
from django.contrib.auth import get_user_model

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'org_code']


class SeatSerializer(serializers.ModelSerializer):
    qr_uuid = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Seat
        fields = ['id', 'identifier', 'qr_uuid']


class WorkspaceSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'type', 'capacity',
            'description', 'amenities', 'available',
            'seats'
        ]


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'type', 'capacity',
            'description', 'amenities', 'available', 'section'
        ]


class SectionSerializer(serializers.ModelSerializer):
    workspaces = WorkspaceSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'capacity', 'location', 'workspaces']


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name', 'capacity', 'location']


class LocationSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'state', 'city', 'address', 'capacity', 'organization', 'sections']


class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'state', 'city', 'address', 'capacity', 'organization']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    seat = SeatSerializer(read_only=True)
    seat_id = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all(), write_only=True, source='seat')

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'seat', 'seat_id',
            'date', 'start_time', 'end_time', 'status', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
