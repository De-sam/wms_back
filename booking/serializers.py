from rest_framework import serializers
from .models import Location, Section, Seat
from users.models import CustomUser  # Adjust if your user model path is different


class SeatSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'uuid']


class SectionSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'capacity', 'seats']

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_superuser and not getattr(user, 'is_org_super_admin', False):
            raise serializers.ValidationError("Only super admins can create sections.")
        return super().create(validated_data)


class LocationSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'state', 'city', 'address', 'capacity', 'sections']

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_superuser and not getattr(user, 'is_org_super_admin', False):
            raise serializers.ValidationError("Only super admins can create locations.")
        return super().create(validated_data)
