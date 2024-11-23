from typing import Any, Dict
from rest_framework.response import Response
from rest_framework import status
class ResponseFormatter:
    
    @staticmethod
    def format_message(
        en: str,
        ar: str,
        status: status,
        data: Any = None,
    ) -> Dict:

        response = {
            "message": {
                "status": status,
                "en": str(en),
                "ar": str(ar),
            }
        }
        
        if data is not None:
            response["data"] = data
            
            
        return response

    @classmethod
    def success_response(
        cls,
        en: str = "Success",
        ar: str = "نجاح",
        status: int = 200,
        data: Any = None
    ) -> Response:
        return Response(
            cls.format_message(en=en, ar=ar, status=status, data=data),
            status=status
        )

    @classmethod
    def error_response(
        cls,
        en: str = "Error",
        ar: str = "خطأ",
        status: int = 400,
        errors: Dict = None
    ) -> Response:
        return Response(
            cls.format_message(en=en, ar=ar, status=status, errors=errors),
            status=status
        )