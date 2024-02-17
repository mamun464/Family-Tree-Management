from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from FamilyApp.serializer import UserRegistrationSerializer 
from rest_framework.response import Response
from rest_framework import status
from FamilyApp.renderers import UserRenderer

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):

        serializer = UserRegistrationSerializer(data=request.data)

        required_fields = ['full_name', 'email', 'phone_no','date_of_birth', 'is_alive','profession','current_address', 'permanent_address']
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token=get_tokens_for_user(user)
            return Response({
                'success': True,
                'status':200,
                'message': 'Registration successful',
                'new_user': serializer.data,
                 'token':token ,
                },status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)