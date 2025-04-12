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

            # Generate and store password temporarily
            plain_password = secrets.token_urlsafe(10)

            # Create inactive user
            super_admin = User.objects.create_user(
                username=f"{organization.subdomain}_admin",
                email=organization.email,
                password=plain_password,  # This gets hashed by Django
                organization=organization,
                is_super_admin=True,
                is_active=False
            )

            # Generate activation token
            token = ActivationToken.objects.create(user=super_admin)

            # Send activation link
            activation_link = f"{settings.FRONTEND_URL}/activate/{token.token}"
            send_mail(
                subject='Activate Your Organization',
                message=f'Click to activate: {activation_link}\nNote: Link expires in 15 minutes.',
                from_email='noreply@example.com',
                recipient_list=[organization.email],
            )

            # Save password temporarily to session or cache (if available)
            request.session[f'password_{super_admin.id}'] = plain_password  # store for 15 mins
            request.session.set_expiry(900)  # 15 minutes

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
