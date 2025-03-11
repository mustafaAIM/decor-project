from .throttlers import ConfigurableThrottle, ProgressiveThrottle
from .registry import ThrottleRegistry

def register_default_policies():
    """Register default throttling policies"""
    
    ThrottleRegistry.register(
        'default',
        ConfigurableThrottle,
        rate='60/min'
    )
    
    ThrottleRegistry.register(
        'auth_endpoints',
        ProgressiveThrottle,
        scope='auth',
        tier_rates={
            0: '5/min',
            1: '3/min',
            2: '1/min',
            3: '1/hour',
            4: '0/day'
        },
        block_durations={
            2: 10,     
            3: 60,     
            4: 1440    
        }
    )
    
    ThrottleRegistry.register(
        'sensitive_ops',
        ProgressiveThrottle,
        scope='sensitive',
        tier_rates={
            0: '10/min',
            1: '5/min',
            2: '2/min',
            3: '1/hour'
        }
    )
    
    ThrottleRegistry.register_for_path(r'^/api/v1/login/?$', 'auth_endpoints')
    ThrottleRegistry.register_for_path(r'^/api/v1/register/?$', 'auth_endpoints')
    ThrottleRegistry.register_for_path(r'^/api/v1/password/reset/?$', 'auth_endpoints')
    ThrottleRegistry.register_for_path(r'^/api/v1/user/profile/?$', 'sensitive_ops') 