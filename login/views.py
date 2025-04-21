from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer #, AdminLoginSerializer
#from rest_framework_simplejwt.tokens import RefreshToken
from users.utils import get_tokens_for_client_user  # ✅ Import the utility
from organizations.models import Organization

class LoginView(APIView):
    def post(self, request, org_code):
        try:
            organization = Organization.objects.get(code=org_code)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = get_tokens_for_client_user(user)  # ✅ Use the utility
            return Response(tokens, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

'''class AdminLoginView(APIView):
    def post(self, request, org_code):
        serializer = AdminLoginSerializer(data=request.data, context={"org_code": org_code})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "email": user.email,
                "organization": user.organization.organization_name
            }, status=200)
        return Response(serializer.errors, status=401)'''
    