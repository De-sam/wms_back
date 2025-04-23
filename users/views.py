from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from organizations.models import Organization
import secrets
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail
from django.conf import settings
#from django.contrib.auth.hashers import make_password
from .models import ClientUser
from rest_framework.permissions import IsAuthenticated
from .serializers import ClientUserSignupSerializer
from django.shortcuts import get_object_or_404

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
            client_user = ClientUser.objects.create_user(
                email=serializer.validated_data['email'],
                full_name=serializer.validated_data['full_name'],
                phone_number=serializer.validated_data['phone_number'],
                password=plain_password,
                organization=organization
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

        # Fetch user's bookings
        bookings = Booking.objects.filter(client_user=client).select_related("workspace")
        booking_data = BookingSummarySerializer(bookings, many=True).data

        return Response({
            "message": "Login successful",
            "client_id": client.id,
            "full_name": client.full_name,
            "email": client.email,
            "phone_number": client.phone_number,
            "notifications_enabled": client.notifications_enabled,
            "bookings": booking_data
        })
    
class ToggleNotificationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, org_code):
        user = request.user

        # Ensure user is a client of the right organization
        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({"detail": "Invalid organization code"}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(user, "organization") or user.organization != organization:
            return Response({"detail": "You do not belong to this organization."}, status=status.HTTP_403_FORBIDDEN)

        user.notifications_enabled = not user.notifications_enabled
        user.save()

        return Response({
            "message": f"Email notifications {'enabled' if user.notifications_enabled else 'disabled'}",
            "notifications_enabled": user.notifications_enabled
        }, status=status.HTTP_200_OK)
    
class GetNotificationStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, org_code):
        user = request.user

        # Check organization match
        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({"detail": "Invalid organization code"}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(user, "organization") or user.organization != organization:
            return Response({"detail": "You do not belong to this organization."}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "notifications_enabled": user.notifications_enabled
        }, status=status.HTTP_200_OK)
    
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class OrganizationUsersView(ListAPIView):
    serializer_class = ClientUserSignupSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        org_code = self.kwargs['org_code']
        organization = get_object_or_404(Organization, code=org_code)
        query = self.request.query_params.get('search', '')

        return ClientUser.objects.filter(
            organization=organization
        ).filter(
            Q(full_name__icontains=query) | Q(email__icontains=query)
        )
# This view handles the signup process for client users.
# It checks if the organization exists, validates the input data,
# and saves the new client user to the database.
# The response includes the created user data or error messages.