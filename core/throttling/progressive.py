class ProgressiveRateThrottle(BaseConfigurableThrottle):
    """
    Throttle that progressively increases restrictions after suspicious activity
    """
    scope = 'progressive'
    
    THROTTLE_TIERS = {
        0: {'rate': '20/min', 'block_duration': 0},    
        1: {'rate': '10/min', 'block_duration': 0},    
        2: {'rate': '5/min', 'block_duration': 5},     
        3: {'rate': '2/min', 'block_duration': 30},    
        4: {'rate': '0/day', 'block_duration': 1440},  
    }
    