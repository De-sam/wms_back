from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from organizations.models import Organization  # Assuming you have an Organization model

class LoginView(APIView):
    def post(self, request, org_code):
        # Validate org_code
        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)

        # Add organization to the request for potential future use (optional)
        request.organization = organization

        # Proceed with normal login
        serializer = LoginSerializer(data=request.data, context={"organization": organization})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
