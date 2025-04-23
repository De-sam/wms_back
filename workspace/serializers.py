from rest_framework import serializers
from .models import Workspace, Booking


class WorkspaceSerializer(serializers.ModelSerializer):
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'type',
            'capacity', 'description', 'amenities', 'is_available'
        ]

class TopBookedWorkspaceSerializer(serializers.ModelSerializer):
    bookings_count = serializers.IntegerField()

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'bookings_count']

class UpcomingBookingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email')
    workspace_name = serializers.CharField(source='workspace.name')
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['user_email', 'workspace_name', 'start_time', 'end_time', 'duration']

    def get_duration(self, obj):
        return str(obj.end_time - obj.start_time)
    
class RecentBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_email = serializers.CharField(source='user__email')
    workspace_name = serializers.CharField(source='workspace__name')
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

class NewWorkspaceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    created_at = serializers.DateTimeField()

class UserSignupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    created_at = serializers.DateTimeField()

class BookingAnalyticsSerializer(serializers.Serializer):
    day = serializers.DateField()
    count = serializers.IntegerField()


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
