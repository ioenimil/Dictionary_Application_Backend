from rest_framework.response import Response
from rest_framework import status

class APIResponseHandler:
    
    @staticmethod
    def api_response(success: bool, data=None, message: str = None, status_code: int = status.HTTP_200_OK):
        response_data = {
            "success": success,
            "message": message or "",
            "data": data or {},
        }
        return Response(response_data, status=status_code)