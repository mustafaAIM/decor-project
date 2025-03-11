from django.core.cache import cache
from .registry import ThrottleRegistry

def track_auth_failure(request, username=None):
    """
    Track an authentication failure, increasing throttling tier
    
    Usage:
    from core.throttling.utils import track_auth_failure
    
    def login_view(request):
        if not authenticate(username, password):
            track_auth_failure(request, username)
            return error_response
    """
    policy = ThrottleRegistry.get_for_path(request.path) or ThrottleRegistry.get_policy('auth_endpoints')
    
    if not policy:
        return
        
    throttle_class = policy['class']
    throttle = throttle_class(**policy['options'])
    
    if username:
        _ = throttle.get_ident
        throttle.get_ident = lambda r: username
        
    throttle.increment_tier(request)


def reset_throttling(request, username=None):
    """Reset throttling state after successful operation"""
    pass