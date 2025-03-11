import traceback
import sys
from typing import Optional
from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import APIException
from .formatters import ResponseFormatter
from .api import BaseAPIException
from rest_framework.response import Response
from core.utils.logger import APILogger

class ErrorDetailExtractor:
    @staticmethod
    def extract_from_dict(detail: dict) -> tuple[Optional[str], str]:
        print(f"\n[Debug] Extracting error from dict: {detail}")
        for field, errors in detail.items():
            if isinstance(errors, list):
                print(f"[Debug] Found list error for field '{field}': {errors[0]}")
                return field, str(errors[0])
            print(f"[Debug] Found string error for field '{field}': {errors}")
            return field, str(errors)
        return None, "Unknown error"

    @staticmethod
    def extract_from_list(detail: list) -> tuple[None, str]:
        print(f"\n[Debug] Extracting error from list: {detail}")
        return None, str(detail[0]) if detail else "Unknown error"

    @classmethod
    def get_error_details(cls, detail) -> tuple[Optional[str], str]:
        print(f"\n[Debug] Getting error details from: {type(detail).__name__}")
        print(f"[Debug] Detail content: {detail}")
        
        if isinstance(detail, dict):
            return cls.extract_from_dict(detail)
        elif isinstance(detail, list):
            return cls.extract_from_list(detail)
        return None, str(detail)

def print_exception_details(exc: Exception, context: dict) -> None:
    """Print detailed exception information for debugging"""
    print("\n" + "="*50)
    print("EXCEPTION DETAILS:")
    print(f"Type: {exc.__class__.__name__}")
    print(f"Message: {str(exc)}")
    
    # Print traceback
    print("\nTRACEBACK:")
    traceback.print_exc()
    
    # Print request details if available
    request = context.get('request')
    if request:
        print("\nREQUEST DETAILS:")
        print(f"Method: {request.method}")
        print(f"Path: {request.path}")
        print(f"Data: {getattr(request, 'data', {})}")
        print(f"Query Params: {getattr(request, 'query_params', {})}")
        print(f"Headers: {dict(request.headers)}")
        
    # Print view details if available
    view = context.get('view')
    if view:
        print(f"\nVIEW: {view.__class__.__name__}")
    
    print("="*50 + "\n")

def custom_exception_handler(exc, context):
    """Global exception handler with improved logging"""
    
    # Log the exception with our pretty logger
    APILogger.log_exception(exc, context)
    
    # Handle BaseAPIException
    if isinstance(exc, BaseAPIException):
        response_data = exc.get_response_data()
        return Response(response_data, status=exc.status_code)

    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        return ResponseFormatter.error(
            en="Validation error",
            ar="خطأ في التحقق",
            status_code=400
        )

    # Handle DRF APIException
    if isinstance(exc, APIException):
        field, message = ErrorDetailExtractor.get_error_details(exc.detail)
        return ResponseFormatter.error(
            en=message,
            ar=message, 
            status_code=exc.status_code,
            field=field
        )

    # Handle unexpected errors
    if exc is not None:
        return ResponseFormatter.error(
            en="Internal server error",
            ar="خطأ في الخادم",
            status_code=500
        )

    return exception_handler(exc, context)
