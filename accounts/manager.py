from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as g
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except:
            raise ValidationError(g("Please enter a Valid email address"))
        
    def create_user(
        self,
        email,
        first_name,
        last_name,
        password,
        **extra_fields
    ):
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(g("Email field can't be empty"))
        
        if not first_name:
            raise ValueError(g("First name field can't be empty"))
        if not last_name:
            raise ValueError(g("Last name field can't be empty"))
        user = self.model(
            email=email,
            first_name=first_name,
            last_name = last_name,
            **extra_fields
        )
        user.set_password(password)
        user. save(using = self._db)
        
        return user
    
    def create_superuser(
        self, 
        email,
        first_name,
        last_name,
        password,
        **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        superuser = self.create_user(
            email,
            first_name,
            last_name,
            password,
            **extra_fields
        )
        superuser.save(using=self._db)
        return superuser
        
  