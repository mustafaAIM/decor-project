class ThrottleRegistry:
    """
    Registry for throttling policies that can be applied globally or to specific paths
    """
    _registry = {}
    _path_specific = {}
    
    @classmethod
    def register(cls, name, throttle_class, **options):
        """Register a named throttling policy"""
        cls._registry[name] = {
            'class': throttle_class,
            'options': options
        }
        
    @classmethod
    def register_for_path(cls, path_pattern, policy_name):
        """Register a throttling policy for a specific URL pattern"""
        cls._path_specific[path_pattern] = policy_name
        
    @classmethod
    def get_policy(cls, name):
        """Retrieve a policy by name"""
        return cls._registry.get(name)
        
    @classmethod
    def get_for_path(cls, path):
        """Get the appropriate policy for a given path"""
        for pattern, policy_name in cls._path_specific.items():
            import re
            if re.match(pattern, path):
                return cls.get_policy(policy_name)
        return None 