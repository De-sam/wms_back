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
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.core.cache import cache

User = get_user_model()


class OrganizationSignupView(APIView):
    def post(self, request):
        org_serializer = OrganizationSignupSerializer(data=request.data)
        if org_serializer.is_valid():
            organization = org_serializer.save()

            # Generate and store password temporarily
            plain_password = secrets.token_urlsafe(10)

            # Create inactive user
            super_admin = User.objects.create_user(
                username=f"{organization.code}_admin",
                email=organization.email,
                password=plain_password,  # This gets hashed by Django
                organization=organization,
                is_super_admin=True,
                is_active=False
            )

            # Generate activation token
            token = ActivationToken.objects.create(user=super_admin, password=plain_password)

            # Send activation link
            activation_link = f"{settings.FRONTEND_URL}activate/{token.token}"
            print(f"Activation link: {activation_link}")  # For debugging
            send_mail(
                subject='Activate Your Organization',
                message=f'Click to activate: {activation_link}\nNote: Link expires in 15 minutes.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[organization.email],
                fail_silently=False,
            )



            return Response({'message': 'Organization created. Activation email sent.'}, status=status.HTTP_201_CREATED)

        return Response(org_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResendActivationTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            organization = Organization.objects.get(email=email)
            user = User.objects.get(email=email, organization=organization, is_super_admin=True)

            if organization.is_active:
                return Response({'detail': 'Organization already activated.'}, status=400)

            # Delete old token if it exists
            ActivationToken.objects.filter(user=user).delete()

            # Create new token
            new_token = ActivationToken.objects.create(user=user)

            # Send new activation link
            activation_link = f"{settings.FRONTEND_URL}activate/{new_token.token}"
            send_mail(
                subject='Resend: Activate Your Organization',
                message=f'Click to activate: {activation_link}\nNote: Link expires in 15 minutes.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )

            return Response({'detail': 'New activation link sent.'}, status=200)

        except Organization.DoesNotExist:
            return Response({'detail': 'Organization not found.'}, status=404)
        except User.DoesNotExist:
            return Response({'detail': 'Super admin not found.'}, status=404)

class ActivateOrganizationView(APIView):
    def get(self, request, token):
        activation_token = get_object_or_404(ActivationToken, token=token)
        user = activation_token.user
        organization = user.organization

        if activation_token.is_expired():
            activation_token.delete()
            return Response({'detail': 'Activation link has expired.'}, status=400)

        if organization.is_active:
            return Response({'detail': 'Organization already activated.'}, status=400)

        # Activate org and super admin
        organization.is_active = True
        organization.save()
        user.is_active = True
        user.save()
        

        # Retrieve plain password from session
        plain_password = activation_token.password
        if not plain_password:
            return Response({'detail': 'Password not found in activation token.'}, status=400)
        if plain_password:
            # Send login credentials
            send_mail(
                subject='Your Organization Login Credentials',
                message=f'Login Email: {user.email}\nPassword: {plain_password}\nURL: {settings.FRONTEND_URL}{organization.code}/login',
                from_email='noreply@example.com',
                recipient_list=[user.email],
            )
        # Delete token
        activation_token.delete()

        return Response({'detail': 'Organization activated and credentials sent.'}, status=200)
    