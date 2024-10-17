from rest_framework import serializers
from .models import User, UserLogout
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from Dictionary.utils.password_validator import validate_password_strength
from Dictionary.utils.error_handler import CustomValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError



class UserSignupSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(min_length=8, write_only=True)
    
    class Meta:
        model = User
        #Check for tuples. Did
        fields = [
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]
        
    def validate(self, attrs):
        password1= attrs.get('password1', '')
        password2= attrs.get('password2', '')
        
        if password1 != password2:
            raise CustomValidationError("Passwords must match")
        
        try:
            validate_password_strength(password1)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password1')
        new_user = User(**validated_data)
        new_user.set_password(password)
        new_user.save()
        return new_user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=50, min_length=6)
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(read_only=True, max_length=100)
    
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    
  
    class Meta:
        model = User
        fields = [
            'email',
            'full_name',
            'password',
            'access_token',
            'refresh_token',

        ]
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(
            request,
            email=email,
            password=password
        )
        if not user:
            raise AuthenticationFailed("Invalid Credentials")
        token = user.tokens()
        
        return {

            'email': user.email,
            'access_token' : str(token.get('access_token')),
            'refresh_token' : str(token.get('refresh_token'))
            
        }


class LogOutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': ("Token is Invalid or has expired")
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')
        # Optional: Add any additional validation here
        return attrs

    def save(self, **kwargs):
        try:
            # Attempt to blacklist the provided refresh token
            token = RefreshToken(self.token)
            user = token['user_id']
            token.blacklist()
            UserLogout.objects.create(user_id=user, logout_time=timezone.now())
            
        except TokenError:
            # If the token is invalid or has expired, return an error
            self.fail('bad_token')

# class BlockUserSerializer(serializers.Serializer):
#     email = serializers.EmailField()

       


