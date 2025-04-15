from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from users.models import ClientUser
from organizations.models import Organization

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        organization = self.context.get("organization")

        try:
            user = ClientUser.objects.get(email=email, organization=organization)
        except ClientUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        data["user"] = user
        return data
