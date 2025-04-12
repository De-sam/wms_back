# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User, Organization, ActivationToken
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
            token = ActivationToken.objects.create(user=super_admin)

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
            activation_link = f"https://wms-front-sable.vercel.app/activate/{token.token}"
            send_mail(
                subject='Activate Your Organization',
                message=f'Click to activate: {activation_link}',
                from_email='noreply@example.com',
                recipient_list=[organization.email],
            )

            return Response({'message': 'Organization created. Activation email sent.'}, status=status.HTTP_201_CREATED)

        return Response(org_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ActivateOrganizationView(APIView):
    def get(self, request, token):
        activation_token = get_object_or_404(ActivationToken, token=token)
        user = activation_token.user
        organization = user.organization

        if organization.is_active:
            return Response({'detail': 'Organization already activated.'}, status=400)

        # Activate both org and super admin
        organization.is_active = True
        organization.save()
        user.is_active = True
        user.save()

        # Send second email with credentials
        send_mail(
            subject='Your Organization Login Credentials',
            message=f'Login Email: {user.email}\nPassword: (the one we generated earlier)',
            from_email='noreply@example.com',
            recipient_list=[user.email],
        )

        # Delete token after use
        activation_token.delete()

        return Response({'detail': 'Organization activated and credentials sent.'}, status=200)
