from django.utils.deprecation import MiddlewareMixin
from organizations.models import Organization

EXCLUDED_PATHS = [
    '/api/organizations/signup/',
    '/api/organizations/activate/',  # Add any other paths to exclude here
]

class OrganizationMiddleware(MiddlewareMixin):
    def __call__(self, request):
        if any(request.path.startswith(path) for path in EXCLUDED_PATHS):
            return self.get_response(request)

        try:
            org_code = request.path.strip('/').split('/')[0]
            organization = Organization.objects.get(code=org_code)
            request.organization = organization
        except (IndexError, Organization.DoesNotExist):
            request.organization = None

        return self.get_response(request)
