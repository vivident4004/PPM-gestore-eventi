from django.urls import path
from .views import RegisterView, custom_logout, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
