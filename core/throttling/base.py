from rest_framework.throttling import SimpleRateThrottle
import logging

logger = logging.getLogger('api.throttling')

class BaseConfigurableThrottle(SimpleRateThrottle):
    """
    Base throttle that provides improved configurability and tracking
    """
    scope = 'configurable'
    cache_format = 'throttle_{scope}_{ident}'
    
    def get_cache_key(self, request, view):
        pass
        
    def throttle_failure_callback(self, request, view):
        """Called when a request is throttled"""
        logger.warning(f"Throttled request from {self.get_ident(request)} to {request.path}")
        return None 