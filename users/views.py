from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from organizations.models import Organization
from .models import ClientUser
from .serializers import ClientUserSignupSerializer

class ClientUserSignupView(APIView):
    def post(self, request, org_code):
        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({'detail': 'Invalid organization code'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClientUserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientUserLoginView(APIView):
    def post(self, request, org_code):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({"error": "Invalid organization"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = ClientUser.objects.get(email=email, organization=organization)
            if not check_password(password, client.password):
                raise ValueError("Incorrect password")
        except (ClientUser.DoesNotExist, ValueError):
            return Response({"non_field_errors": ["Invalid email or password"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Login successful",
            "client_id": client.id,
            "full_name": client.full_name
        })
# This view handles the signup process for client users.
# It checks if the organization exists, validates the input data,
# and saves the new client user to the database.
# The response includes the created user data or error messages.