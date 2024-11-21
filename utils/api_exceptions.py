from rest_framework.exceptions import APIException
from rest_framework import status
from typing import Optional, Dict, Any

class APIError(APIException):
    """Base API Exception class for handling all 4xx errors"""
    
    def __init__(
        self,
        en_message: str,
        ar_message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        self.en_message = en_message
        self.ar_message = ar_message
        self.status_code = status_code
        self.error_code = error_code or str(status_code)
        self.extra_data = extra_data
        super().__init__(detail=None)

# Common 4xx error classes
class BadRequestError(APIError):
    def __init__(self, en_message: str, ar_message: str, **kwargs):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs
        )

class AuthenticationError(APIError):
    def __init__(self, en_message: str = "Authentication failed", ar_message: str = "فشل المصادقة", **kwargs):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )

class PermissionError(APIError):
    def __init__(self, en_message: str = "Permission denied", ar_message: str = "تم رفض الإذن", **kwargs):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs
        )

class NotFoundError(APIError):
    def __init__(self, en_message: str = "Resource not found", ar_message: str = "المورد غير موجود", **kwargs):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs
        ) 