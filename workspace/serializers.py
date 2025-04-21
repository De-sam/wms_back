from rest_framework import serializers
from .models import Section, Workspace, Booking


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']


class WorkspaceSerializer(serializers.ModelSerializer):
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = Workspace
        fields = [
            'id', 'section', 'name', 'type',
            'capacity', 'description', 'amenities', 'is_available'
        ]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'workspace', 'user', 'start_time', 'end_time']
        read_only_fields = ['user']

    def validate(self, data):
        workspace = data['workspace']
        start_time = data['start_time']
        end_time = data['end_time']

        overlapping = Booking.objects.filter(
            workspace=workspace,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if overlapping.exists():
            raise serializers.ValidationError("This workspace is already booked for the selected time range.")
        return data
