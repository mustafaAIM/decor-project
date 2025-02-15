from typing import Any, Optional, Dict
from rest_framework.response import Response

class ResponseFormatter:
    @staticmethod
    def format_error(en: str, ar: str, field: Optional[str] = None) -> dict:
        data = {
            "status": "error",
            "en": str(en),
            "ar": str(ar)
        }
        if field:
            data["field"] = field
        return data

    @staticmethod
    def format_success(data: Any = None, message: Optional[Dict] = None) -> dict:
        response = {
            "status": "success",
        }
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return response

    @classmethod
    def error_response(
        cls,
        en: str,
        ar: str,
        status_code: int = 400,
        field: Optional[str] = None
    ) -> Response:
        return Response(
            cls.format_error(en=en, ar=ar, field=field),
            status=status_code
        )

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        status_code: int = 200,
        message: Optional[Dict] = None
    ) -> Response:
        return Response(
            cls.format_success(data, message),
            status=status_code
        )

# Common messages that can be reused across the application
class Messages:
    class Search:
        NO_RESULTS = {
            'en': 'No products found matching your search criteria.',
            'ar': 'لم يتم العثور على منتجات تطابق معايير البحث.'
        }
        INVALID_SEARCH = {
            'en': 'Invalid search parameters provided.',
            'ar': 'معايير البحث غير صالحة.'
        } 