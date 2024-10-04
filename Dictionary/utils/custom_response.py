from rest_framework.response import Response
from rest_framework import status

def api_response(success, data=None, message=None, status_code=status.HTTP_200_OK):
    return Response({
        "success" : success,
        "message": message,
        "data": data
    }, status=status_code)