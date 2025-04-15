from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from organizations.models import Organization
import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import ClientUser
from .serializers import ClientUserSignupSerializer

class ClientUserSignupView(APIView):
    def post(self, request, org_code):
        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({'detail': 'Invalid organization code'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClientUserSignupSerializer(data=request.data, context={'organization': organization})
        if serializer.is_valid():
            # Generate a secure random password
            plain_password = secrets.token_urlsafe(10)

            # Save the client with a hashed password
            client_user = ClientUser.objects.create(
                organization=organization,
                full_name=serializer.validated_data['full_name'],
                email=serializer.validated_data['email'],
                phone_number=serializer.validated_data['phone_number'],
                password=make_password(plain_password)
            )

            # Send login credentials via email
            send_mail(
                subject='Your Client Login Credentials',
                message=f"Hello {client_user.full_name},\n\n"
                        f"Here are your login details:\n"
                        f"Email: {client_user.email}\n"
                        f"Password: {plain_password}\n"
                        f"Login here: {settings.FRONTEND_URL}{organization.code}/login\n\n"
                        f"Please keep this information secure.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client_user.email],
                fail_silently=False,
            )

            return Response({'message': 'Client created and credentials sent via email.'}, status=status.HTTP_201_CREATED)

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