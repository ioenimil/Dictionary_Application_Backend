from rest_framework import serializers
from .error_handler import CustomValidationError

def validate_password_strength(password):

    if not any(char.isdigit() for char in password):
        raise CustomValidationError("Password must contain at least one digit")
    if not any(char.isupper() for char in password):
        raise CustomValidationError("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        raise CustomValidationError("Password must contain at least one lowercase letter.")
    if not any(char in "!@#$%^&*()-_+=<>?/.,:;" for char in password):
        raise CustomValidationError("Password must contain at least one special character.")
