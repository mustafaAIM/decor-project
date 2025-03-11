from core.utils.logger import APILogger

class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            APILogger.log_request(request)

        response = self.get_response(request)

        if request.path.startswith('/api/'):
            APILogger.log_response(response)

        return response 