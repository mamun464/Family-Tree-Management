
# from django.contrib import admin
from django.urls import path
# from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from FamilyApp.views import UserRegistrationView,UserLoginView,PhotoUpload,UserProfileView,UserEditView,UserDeleteView,UserPasswordChangeView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('upload-dp/', PhotoUpload.as_view(),name='PhotoUpload'),
    path('profile/', UserProfileView.as_view(),name='profile'),
    path('update/', UserEditView.as_view(),name='edit-user'),
    path('delete/', UserDeleteView.as_view(),name='delete-user'),
    path('changepassword/', UserPasswordChangeView.as_view(),name='passwordChange'),
    # path('event-register/', EventEnrollmentView.as_view(), name='event-register'),
    # path('event-deregister/', EventDeregistration.as_view(), name='event-deregister'),
    # path('events/', UserEvents.as_view(), name='events'),
    
    
]
