# middlewares.py
from django.http import JsonResponse
from organizations.models import Organization

class OrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        org_code = request.path.split('/')[1]  # Extract the org_code from the URL
        try:
            organization = Organization.objects.get(code=org_code)
            request.organization = organization  # Make organization available in the request
        except Organization.DoesNotExist:
            return JsonResponse({"detail": "Organization not found"}, status=404)

        response = self.get_response(request)
        return response
