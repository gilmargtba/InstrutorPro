from rest_framework.views import exception_handler


def stable_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    request = context.get("request")
    request_id = getattr(request, "request_id", None)
    details = response.data
    code = getattr(exc, "default_code", "request_error")
    message = getattr(exc, "default_detail", "Não foi possível processar a solicitação.")
    response.data = {
        "error": {
            "code": str(code).upper(),
            "message": str(message),
            "details": details,
            "request_id": request_id,
        }
    }
    return response
