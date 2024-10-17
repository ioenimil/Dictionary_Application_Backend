from django.db import models


# Create your models here.
import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as g
from .manager import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# from datetime import datetime

# Create your models here.
AUTH_PROVIDERS = {
    'email': 'email',
    
    
}

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name=(g('Email Address')))
    first_name = models.CharField(max_length=50, verbose_name=(g('First Name')))
    last_name = models.CharField(max_length=50, verbose_name=(g("Last Name")))
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get("email"))
    
    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = [
        'first_name',
        'last_name'
    ]
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.first_name
    
    @property
    def get_email(self):
        return f'{self.email}'
    
    @property
    def get_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def tokens(self):
       refresh_token = RefreshToken.for_user(self)
       return {
           'refresh_token': str(refresh_token),
           'access_token': str(refresh_token.access_token)
       } 
       
class UserLogout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    logout_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} logged out at {self.logout_time}"
 