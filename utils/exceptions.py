from rest_framework.exceptions import APIException
from rest_framework import status
from typing import Optional, Any, Dict

class BaseCustomException(APIException):
    def __init__(
        self,
        en_message: str,
        ar_message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        self.en_message = en_message
        self.ar_message = ar_message
        self.status_code = status_code
        self.extra_data = extra_data
        super().__init__(detail=None)

class ValidationError(BaseCustomException):
    def __init__(
        self,
        en_message: str = "Validation error",
        ar_message: str = "خطأ في التحقق",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_400_BAD_REQUEST,
            extra_data=extra_data
        )

class NotFoundError(BaseCustomException):
    """Exception raised when a resource is not found"""
    
    def __init__(
        self,
        en_message: str = "Resource not found",
        ar_message: str = "المورد غير موجود",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_404_NOT_FOUND,
            extra_data=extra_data
        )

class UnauthorizedError(BaseCustomException):
    """Exception raised for authentication errors"""
    
    def __init__(
        self,
        en_message: str = "Unauthorized access",
        ar_message: str = "غير مصرح به",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            extra_data=extra_data
        )

class PermissionDeniedError(BaseCustomException):
    """Exception raised for permission errors"""
    
    def __init__(
        self,
        en_message: str = "Permission denied",
        ar_message: str = "تم رفض الإذن",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_403_FORBIDDEN,
            extra_data=extra_data
        )