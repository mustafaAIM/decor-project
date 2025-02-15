from rest_framework.exceptions import APIException
from rest_framework import status

class BaseAPIException(APIException):
    """Base API Exception class with i18n support"""
    def __init__(self, en_message: str, ar_message: str, status_code: int, field: str = None):
        self.en_message = en_message
        self.ar_message = ar_message
        self.status_code = status_code
        self.field = field
        super().__init__(detail=None)

    def get_response_data(self):
        data = {
            "status": "error",
            "en": self.en_message,
            "ar": self.ar_message
        }
        if self.field:
            data["field"] = self.field
        return data

class BadRequestException(BaseAPIException):
    def __init__(self, en_message: str, ar_message: str, field: str = None):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_400_BAD_REQUEST,
            field=field
        )

class AuthenticationException(BaseAPIException):
    def __init__(self, en_message: str = "Authentication failed", ar_message: str = "فشل المصادقة"):
        super().__init__(
            en_message=en_message,
            ar_message=ar_message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

# ... other exception classes ...
