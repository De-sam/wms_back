from rest_framework import serializers
from .models import ClientUser

class ClientUserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = ['full_name', 'email', 'phone_number']

    def validate_email(self, value):
        """
        Check if the email is already registered for the organization.
        """
        organization = self.context['organization']
        if ClientUser.objects.filter(organization=organization, email=value).exists():
            raise serializers.ValidationError("Email is already registered for this organization.")
        return value
    
    def create(self, validated_data):
        """
        Create a new ClientUser instance.
        """
        organization = self.context['organization']
        client_user = ClientUser.objects.create(organization=organization, **validated_data)
        return client_user
    
    def update(self, instance, validated_data):
        """
        Update an existing ClientUser instance.
        """
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance
    
    def validate(self, data):
        """
        Perform additional validation on the input data.
        """
        if not data.get('full_name'):
            raise serializers.ValidationError("Full name is required.")
        if not data.get('email'):
            raise serializers.ValidationError("Email is required.")
        if not data.get('phone_number'):
            raise serializers.ValidationError("Phone number is required.")
        return data
