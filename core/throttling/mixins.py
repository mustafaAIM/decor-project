class ThrottleTrackingMixin:
    """
    Mixin for views to track throttling events, especially authentication failures
    """
    def track_auth_failure(self, request):
        """Increase throttling tier after authentication failure"""
        
    def track_auth_success(self, request):
        """Reset or reduce throttling tier after successful authentication"""
        