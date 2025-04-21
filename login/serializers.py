from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from users.models import ClientUser
from organizations.models import Organization, User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    org_code = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        org_code = data.get('org_code')
        
        try:
            # Check if the organization exists
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            raise serializers.ValidationError('Invalid organization code')

        try:
            # Check if the user exists within the organization
            if ClientUser.objects.filter(email=email, organization=organization).exists():
                user = ClientUser.objects.get(email=email, organization=organization)
            elif User.objects.filter(email=email, organization=organization).exists():
                user = User.objects.get(email=email, organization=organization)
            else:
                raise serializers.ValidationError('User does not exist')
        except ClientUser.DoesNotExist:
            raise serializers.ValidationError('User does not exist')

        # Validate the password
        if not check_password(password, user.password):
            raise serializers.ValidationError('Invalid password')

        # Return validated data
        return {
            'email': user.email,
            'organization': organization.name,
            'user_id': user.id
        }
