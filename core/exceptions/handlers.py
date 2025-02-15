from typing import Optional
from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import APIException
from .formatters import ResponseFormatter
from .api import BaseAPIException
from rest_framework.response import Response

class ErrorDetailExtractor:
    @staticmethod
    def extract_from_dict(detail: dict) -> tuple[Optional[str], str]:
        for field, errors in detail.items():
            if isinstance(errors, list):
                return field, str(errors[0])
            return field, str(errors)
        return None, "Unknown error"

    @staticmethod
    def extract_from_list(detail: list) -> tuple[None, str]:
        return None, str(detail[0]) if detail else "Unknown error"

    @classmethod
    def get_error_details(cls, detail) -> tuple[Optional[str], str]:
        if isinstance(detail, dict):
            return cls.extract_from_dict(detail)
        elif isinstance(detail, list):
            return cls.extract_from_list(detail)
        return None, str(detail)

def custom_exception_handler(exc, context):
    
    if isinstance(exc, BaseAPIException):
        return Response(exc.get_response_data(), status=exc.status_code)

    if isinstance(exc, DjangoValidationError):
        return ResponseFormatter.error(
            en="Validation error",
            ar="خطأ في التحقق",
            status_code=400
        )

    if isinstance(exc, APIException):
        field, message = ErrorDetailExtractor.get_error_details(exc.detail)
        return ResponseFormatter.error(
            en=message,
            ar=message, 
            status_code=exc.status_code,
            field=field
        )

    if exc is not None:
        return ResponseFormatter.error(
            en="Internal server error",
            ar="خطأ في الخادم",
            status_code=500
        )

    return exception_handler(exc, context)
