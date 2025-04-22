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
        fields = '__all__'

    def validate(self, data):
        start = data.get('start_time')
        end = data.get('end_time')
        workspace = data.get('workspace')

        conflict = Booking.objects.filter(
            workspace=workspace,
            status='ACTIVE',
        ).filter(
            Q(start_time__lt=end) & Q(end_time__gt=start)
        ).exists()

        if conflict:
            raise serializers.ValidationError("This workspace is already booked for the selected time.")
        return data

class BookingSummarySerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source='workspace.name')

    class Meta:
        model = Booking
        fields = ['workspace_name', 'start_time', 'end_time', 'status']
