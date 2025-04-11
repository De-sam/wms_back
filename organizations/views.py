# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import OrganizationSignupSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import secrets

User = get_user_model()


class OrganizationSignupView(APIView):
    def post(self, request):
        org_serializer = OrganizationSignupSerializer(data=request.data)
        if org_serializer.is_valid():
            organization = org_serializer.save()

            # Create super admin user with random password
            password = secrets.token_urlsafe(10)
            super_admin = User.objects.create_user(
                username=f"{organization.subdomain}_admin",
                email=organization.email,
                password=password,
                organization=organization,
                is_super_admin=True,
                is_active=False  # Activate after email verification
            )

            # Send activation email (with fake link placeholder for now)
            activation_link = f"https://wms-front-sable.vercel.app/activate/{organization.subdomain}"
            send_mail(
                subject='Activate Your Organization',
                message=f'Click to activate: {activation_link}',
                from_email='noreply@example.com',
                recipient_list=[organization.email],
            )

            return Response({'message': 'Organization created. Activation email sent.'}, status=status.HTTP_201_CREATED)

        return Response(org_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
