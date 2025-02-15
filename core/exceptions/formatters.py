from rest_framework.response import Response
from typing import Any, Optional

class ResponseFormatter:
    @staticmethod
    def error(
        en: str,
        ar: str,
        status_code: int = 400,
        field: Optional[str] = None
    ) -> Response:
        data = {
            "status": "error",
            "en": str(en),
            "ar": str(ar)
        }
        if field:
            data["field"] = field
        return Response(data, status=status_code)

    @staticmethod
    def success(
        data: Any = None,
        status_code: int = 200,
        message: Optional[dict] = None
    ) -> Response:
        response_data = {"status": "success"}
        if data is not None:
            response_data["data"] = data
        if message:
            response_data["message"] = message
        return Response(response_data, status=status_code)
