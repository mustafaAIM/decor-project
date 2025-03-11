from django.http import HttpResponse
from rest_framework.response import Response
from django.urls import resolve
from django.conf import settings
from .registry import ThrottleRegistry
import json
import time

class ThrottlingMiddleware:
    """
    Middleware that applies throttling policies based on request path and method
    without requiring view modifications
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if any(request.path.startswith(path) for path in getattr(settings, 'THROTTLE_EXCLUDED_PATHS', [])):
            return self.get_response(request)
            
        policy = ThrottleRegistry.get_for_path(request.path)
        
        if not policy:
            policy = ThrottleRegistry.get_policy('default')
            
        if not policy:
            return self.get_response(request)
        
        throttle_class = policy['class']
        throttle_instance = throttle_class(**policy['options'])
        
        allowed = throttle_instance.allow_request(request)
        
        if allowed:
            return self.get_response(request)
        else:
            response_data = {
                'detail': 'Request was throttled',
                'retry_after': throttle_instance.wait()
            }
            
            if hasattr(request, '_request') and hasattr(request._request, 'accepted_renderer'):
                return Response(response_data, status=429)
            else:
                return HttpResponse(
                    json.dumps(response_data),
                    status=429,
                    content_type='application/json'
                ) 