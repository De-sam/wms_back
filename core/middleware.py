class OrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path_parts = request.path.strip("/").split("/")
        if path_parts and path_parts[0].isdigit() and len(path_parts[0]) == 6:
            request.org_code = path_parts[0]
        else:
            request.org_code = None
        return self.get_response(request)
