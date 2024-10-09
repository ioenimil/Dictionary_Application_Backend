from django.urls import path
from .views import UserRegisterView, LoginView    


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'), 
]