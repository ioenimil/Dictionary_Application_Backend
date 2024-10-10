from Dictionary.utils.custom_response import APIResponseHandler
from rest_framework.exceptions import ValidationError
# from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSignupSerializer, UserLoginSerializer

class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        try:
             
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                return Response({
                    'message' : "User Registration Successful"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:  
            return APIResponseHandler.api_response(
                success=False,
                message="Registration failed. Please correct the following errors:",
                data=serializer.errors,  
                status_code=status.HTTP_400_BAD_REQUEST
        )

    
        
class LoginView(APIView):   
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        try:
            if serializer.is_valid(raise_exception=True):
                return APIResponseHandler.api_response(
                    success=True,
                    message="Logged in Successfully",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )
        
        
        except ValidationError as ve:
            return APIResponseHandler.api_response(
                success=False,
                message="Login failed. Invalid Credentials.",
                data=serializer.errors, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        
        except Exception as e:
            return APIResponseHandler.api_response(
                success=False,
                message=f"Login failed due to an unexpected error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )