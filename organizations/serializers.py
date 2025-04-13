from rest_framework import serializers
from .models import Organization, User


class OrganizationSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['organization_name', 'email']

    def create(self, validated_data):
        return Organization.objects.create(**validated_data)
