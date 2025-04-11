from rest_framework import serializers
from .models import Organization, User
from django.utils.text import slugify


class OrganizationSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['organization_name', 'email']

    def create(self, validated_data):
        # Generate a unique subdomain
        base_subdomain = slugify(validated_data['organization_name'])
        # Ensure the subdomain is unique    
        subdomain = base_subdomain
        count = 1
        while Organization.objects.filter(subdomain=subdomain).exists():
            subdomain = f"{base_subdomain}{count}"
            count += 1
        validated_data['subdomain'] = subdomain

        return Organization.objects.create(**validated_data)
