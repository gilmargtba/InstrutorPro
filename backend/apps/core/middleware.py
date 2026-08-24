import uuid

REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        candidate = request.META.get(REQUEST_ID_HEADER)
        try:
            request_id = str(uuid.UUID(candidate)) if candidate else str(uuid.uuid4())
        except (ValueError, AttributeError, TypeError):
            request_id = str(uuid.uuid4())
        request.request_id = request_id
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
