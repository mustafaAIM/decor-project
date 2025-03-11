from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache
from datetime import datetime, timedelta
import time

class ConfigurableThrottle(SimpleRateThrottle):
    """Configurable rate throttle that can be instantiated with options"""
    scope = 'configurable'
    
    def __init__(self, **options):
        self.rate = options.get('rate', '10/day')
        self.scope = options.get('scope', self.scope)
        
        # Support for progressive throttling
        self.tier_rates = options.get('tier_rates', {})
        self.block_durations = options.get('block_durations', {})
        
        super().__init__()
    
    def get_cache_key(self, request, view=None):
        ident = self.get_ident(request)
        return f'throttle_{self.scope}_{ident}'
    
    def allow_request(self, request, view=None):
        # Check for blocks first
        if self.is_blocked(request):
            return False
            
        # If using tiers, get the current tier and apply appropriate rate
        if self.tier_rates:
            tier = self.get_current_tier(request)
            if tier in self.tier_rates:
                self.rate = self.tier_rates[tier]
                
        # Continue with normal throttling
        return super().allow_request(request, view)
    
    def is_blocked(self, request):
        """Check if the request is currently blocked"""
        cache_key = f"{self.get_cache_key(request)}_blocked_until"
        blocked_until = cache.get(cache_key)
        
        if blocked_until:
            return datetime.now() < blocked_until
        return False
    
    def get_current_tier(self, request):
        """Get the current throttling tier for this request"""
        cache_key = f"{self.get_cache_key(request)}_tier"
        return cache.get(cache_key, 0)
    
    def increment_tier(self, request):
        """Increment the throttling tier and apply blocks if needed"""
        cache_key = f"{self.get_cache_key(request)}_tier"
        current_tier = cache.get(cache_key, 0)
        new_tier = min(current_tier + 1, max(self.tier_rates.keys(), default=0))
        
        # Save the new tier
        cache.set(cache_key, new_tier, 24*60*60)  # 24 hour expiration
        
        # Apply block if configured for this tier
        if new_tier in self.block_durations and self.block_durations[new_tier] > 0:
            block_minutes = self.block_durations[new_tier]
            blocked_until = datetime.now() + timedelta(minutes=block_minutes)
            block_key = f"{self.get_cache_key(request)}_blocked_until"
            cache.set(block_key, blocked_until, block_minutes*60)
            
        return new_tier


class ProgressiveThrottle(ConfigurableThrottle):
    """Pre-configured throttle that increases restrictions progressively"""
    scope = 'progressive'
    
    def __init__(self, **options):
        default_options = {
            'tier_rates': {
                0: '20/min',  # Normal operation
                1: '10/min',  # After first violation
                2: '5/min',   # After second violation
                3: '2/min',   # After third violation
                4: '1/hour',  # After fourth violation
            },
            'block_durations': {
                0: 0,         # No block
                1: 0,         # No block
                2: 5,         # 5 minute block
                3: 30,        # 30 minute block
                4: 1440,      # 24 hour block
            }
        }
        
        # Override defaults with any provided options
        default_options.update(options)
        
        super().__init__(**default_options) 