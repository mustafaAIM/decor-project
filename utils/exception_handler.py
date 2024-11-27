from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import APIException
from utils.messages import ResponseFormatter

def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats all errors consistently
    """
    try:
        status_code = exc.status_code
    except AttributeError:
        status_code = 400

    if isinstance(exc, DjangoValidationError):
        return ResponseFormatter.error_response(
            en="Validation error",
            ar="خطأ في التحقق",
            status_code=400
        )

    if isinstance(exc, APIException):
        if hasattr(exc, 'en_message') and hasattr(exc, 'ar_message'):
            return ResponseFormatter.error_response(
                en=exc.en_message,
                ar=exc.ar_message,
                status_code=status_code
            )
        else:
            return ResponseFormatter.error_response(
                en=str(exc.detail),
                ar=str(exc.detail),
                status_code=status_code
            )

    if exc is not None:
        return ResponseFormatter.error_response(
            en="Internal server error",
            ar="خطأ في الخادم",
            status_code=500
        )

    return exception_handler(exc, context)