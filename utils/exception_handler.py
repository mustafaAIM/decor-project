from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import (
    APIException,
    ValidationError as DRFValidationError
)
from utils.api_exceptions import APIError
from typing import Optional, Dict, Any

def format_error_response(
    status_code: int,
    en_message: str,
    ar_message: str,
    error_code: Optional[str] = None,
    errors: Optional[Dict[str, Any]] = None
) -> Dict:
    """Format error response consistently"""
    response = {
        "message": {
            "status": error_code or str(status_code),
            "en": en_message,
            "ar": ar_message,
        }
    }
    if errors:
        response["errors"] = errors
    return response

def custom_exception_handler(exc, context):
    """
    Custom exception handler that:
    - Standardizes all 4xx error responses
    - Lets 5xx errors pass through normally
    - Maintains DRF's browsable API functionality
    """
    
    # Get the standard DRF exception response
    response = exception_handler(exc, context)
    
    # Handle 5xx errors normally
    if isinstance(exc, Exception) and not isinstance(exc, APIException):
        return response

    try:
        status_code = exc.status_code
    except AttributeError:
        status_code = status.HTTP_400_BAD_REQUEST

    # Don't format 5xx errors
    if status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        return response

    # Handle our custom API errors
    if isinstance(exc, APIError):
        data = format_error_response(
            status_code=exc.status_code,
            en_message=exc.en_message,
            ar_message=exc.ar_message,
            error_code=exc.error_code,
            errors=exc.extra_data
        )
        return Response(data, status=status_code)

    # Handle DRF ValidationError
    if isinstance(exc, DRFValidationError):
        data = format_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            en_message="Validation error",
            ar_message="خطأ في التحقق",
            errors=exc.detail
        )
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        data = format_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            en_message="Validation error",
            ar_message="خطأ في التحقق",
            errors=exc.messages if hasattr(exc, 'messages') else str(exc)
        )
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Handle any other 4xx errors
    if response is not None and 400 <= status_code < 500:
        data = format_error_response(
            status_code=status_code,
            en_message=str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            ar_message=str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        )
        return Response(data, status=status_code)

    return response