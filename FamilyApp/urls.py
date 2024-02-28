
# from django.contrib import admin
from django.urls import path
# from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from FamilyApp.views import UserRegistrationView,UserLoginView,PhotoUpload,UserProfileView,UserEditView,UserDeleteView,RemoveConnectionView,UserPasswordChangeView,CreateConnectionView,UserConnectionsView,FamilyMemberSearchAPIView,AllMemberListView,MemberProfileView,AncestorsView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('upload-dp/', PhotoUpload.as_view(),name='PhotoUpload'),
    path('profile/', UserProfileView.as_view(),name='profile'),
    path('single/', MemberProfileView.as_view(), name='member_detail'),
    path('all/', AllMemberListView.as_view(),name='profile'),
    path('update/', UserEditView.as_view(),name='edit-user'),
    path('delete/', UserDeleteView.as_view(),name='delete-user'),
    path('changepassword/', UserPasswordChangeView.as_view(),name='passwordChange'),
    path('create-connection/', CreateConnectionView.as_view(), name='create_connection'),
    path('disconnected/', RemoveConnectionView.as_view(), name='remove_connection'),
    path('member-connections/', UserConnectionsView.as_view(), name='user_connections'),
    path('search/', FamilyMemberSearchAPIView.as_view(), name='family_member_search'),
    path('ancestors/', AncestorsView.as_view(), name='ancestors'),

    # path('event-register/', EventEnrollmentView.as_view(), name='event-register'),
    # path('event-deregister/', EventDeregistration.as_view(), name='event-deregister'),
    # path('events/', UserEvents.as_view(), name='events'),
    
    
]
