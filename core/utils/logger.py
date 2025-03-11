import logging
import json
from django.utils.termcolors import colorize
from typing import Any, Dict, Optional

class APILogger:
    """Enhanced logger for API requests/responses with color formatting"""
    
    COLORS = {
        'ERROR': 'red',
        'WARNING': 'yellow',
        'INFO': 'green',
        'DEBUG': 'blue',
        'REQUEST': 'magenta', 
        'RESPONSE': 'cyan',
        'VALIDATION': 'yellow',
    }
    
    @staticmethod
    def format_dict(data: Dict[str, Any], indent: int = 2) -> str:
        """Format dictionary as indented JSON string"""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(data)
    
    @classmethod
    def log_request(cls, request) -> None:
        method = colorize(request.method, fg='white', opts=('bold',))
        path = colorize(request.path, fg='white')
        
        print("\n" + "="*80)
        print(colorize(" 📥 REQUEST ", fg=cls.COLORS['REQUEST'], opts=('bold',)))
        print(f" {method} {path}")
        
        if hasattr(request, 'headers'):
            print(colorize("\n Headers:", fg=cls.COLORS['REQUEST']))
            for key, value in dict(request.headers).items():
                if key.lower() not in ('cookie', 'authorization'):
                    print(f"   {key}: {value}")
                else:
                    print(f"   {key}: [FILTERED]")
        
        if hasattr(request, 'data') and request.data:
            print(colorize("\n Data:", fg=cls.COLORS['REQUEST']))
            print(f"   {cls.format_dict(request.data)}")
            
        if hasattr(request, 'query_params') and request.query_params:
            print(colorize("\n Query Params:", fg=cls.COLORS['REQUEST']))
            print(f"   {cls.format_dict(dict(request.query_params))}")
    
    @classmethod
    def log_response(cls, response) -> None:
        status = response.status_code
        status_color = 'green' if 200 <= status < 300 else 'red'
        
        print("\n" + "-"*80)
        print(colorize(f" 📤 RESPONSE (HTTP {status})", fg=cls.COLORS['RESPONSE'], opts=('bold',)))
        
        if hasattr(response, 'data'):
            print(colorize("\n Response Data:", fg=cls.COLORS['RESPONSE']))
            print(f"   {cls.format_dict(response.data)}")
        print("="*80 + "\n")
    
    @classmethod
    def log_exception(cls, exc, context=None) -> None:
        """Log exception with traceback and request details"""
        import traceback
        
        print("\n" + "="*80)
        print(colorize(f" 🚨 EXCEPTION: {exc.__class__.__name__}", fg=cls.COLORS['ERROR'], opts=('bold',)))
        print(colorize(f" {str(exc)}", fg=cls.COLORS['ERROR']))
        
        print(colorize("\n Traceback:", fg=cls.COLORS['ERROR']))
        tb_lines = traceback.format_exc().split('\n')
        if len(tb_lines) > 10:
            print('   ...')
            print('\n'.join('   ' + line for line in tb_lines[-10:]))
        else:
            print('\n'.join('   ' + line for line in tb_lines))
        
        if context and 'request' in context:
            cls.log_request(context['request']) 