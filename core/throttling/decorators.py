from functools import wraps
from django.http import HttpResponse
from rest_framework.response import Response
import json
from .registry import ThrottleRegistry

def throttle(policy_name=None, **options):
    """
    Decorator to apply throttling to a view or viewset method
    
    @throttle('auth_endpoints')
    def post(self, request):
        # Your view logic
        
    @throttle(rate='5/min', block_duration=10)
    def post(self, request):
        # Your view logic
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            if policy_name and not options:
                policy = ThrottleRegistry.get_policy(policy_name)
                if policy:
                    throttle_class = policy['class']
                    throttle_instance = throttle_class(**policy['options'])
                else:
                    from .throttlers import ConfigurableThrottle
                    throttle_instance = ConfigurableThrottle(**options)
            else:
                from .throttlers import ConfigurableThrottle
                throttle_instance = ConfigurableThrottle(**options)
            
            allowed = throttle_instance.allow_request(request)
            
            if allowed:
                return view_func(self, request, *args, **kwargs)
            else:
                response_data = {
                    'detail': 'Request was throttled',
                    'retry_after': throttle_instance.wait()
                }
                
                return Response(response_data, status=429)
                
        return wrapped_view
    return decorator 