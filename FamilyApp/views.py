from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from FamilyApp.serializer import UserRegistrationSerializer ,UserLoginSerializer,UserProfileEditSerializer
from rest_framework.response import Response
from rest_framework import status
from FamilyApp.renderers import UserRenderer
from django.utils import timezone
from django.contrib.auth import authenticate,login
from FamilyApp.models import FamilyMember
from rest_framework.permissions import IsAuthenticated,IsAdminUser
import requests

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

        required_fields = ['full_name', 'email', 'phone_no','date_of_birth','password', 'password2']
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            user = serializer.save()
            token=get_tokens_for_user(user)
            return Response({
                'success': True,
                'status':200,
                'message': 'Registration successful',
                'new_user': serializer.data,
                 'token':token ,
                },status=status.HTTP_201_CREATED)
        else:
            errors = serializer.errors
            error_messages = {}
            for field, message in errors.items():
                error_messages[field] = message[0]  # Only take the first error message
            return Response({
                "success": False,
                "status": 400,
                "message": error_messages
            }, status=status.HTTP_400_BAD_REQUEST)
        

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        
        serializer = UserLoginSerializer(data=request.data)
        required_fields = ['phone_no','password']

        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)    


        if serializer.is_valid(raise_exception=True):
            # Access both the authenticated user and validated data from the serializer
            validated_data = serializer.validated_data
            user = validated_data['user']

            # Your existing logic here
            user.last_login = timezone.now()
            user.save()
            # Log the user in (if needed)
            login(request, user)
            token=get_tokens_for_user(user)
            return Response({
                'msg': 'Login successful',
                'token':token,
                },status=status.HTTP_200_OK)

        else:
            errors = serializer.errors
            error_messages = {}
            for field, message in errors.items():
                error_messages[field] = message[0]  # Only take the first error message
            return Response({
                "success": False,
                "status": 400,
                "message": ""
            }, status=status.HTTP_400_BAD_REQUEST)
        

class PhotoUpload(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    
    def upload_to_imagebb(self, api_key, image_data):
        api_url = "https://api.imgbb.com/1/upload"
        files = {"image": image_data}
        params = {"key": api_key}

        response = requests.post(api_url, files=files, params=params)

        try:
            result = response.json()

            # Check if the upload was successful
            if result['success']:
                return result["data"]["url"]

            # If not successful, handle the error
            error_msg = result.get("error", "Unknown error")
            print("Error in JSON response:", error_msg)
        except ValueError:
            # If the content is not in JSON format, print the raw content
            print("Non-JSON response content:", response.content)

        return None

    def put(self, request):

        required_fields = ['user_profile_img']

        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)  
            
        serializer = UserProfileEditSerializer(request.user)
        userData=serializer.data
        user_id = userData['id']
        
        try:
            user = FamilyMember.objects.get(id=user_id)
        except FamilyMember.DoesNotExist:
            return Response({
                    'success': False,
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f"User Not Found or Invalid User",
                }, status=status.HTTP_404_NOT_FOUND) 
            

        # Check if 'user_profile_img' key is present in the request data
        if 'user_profile_img' in request.data:
            # Assuming you have an image file in the request data
            image_file = request.data.get("user_profile_img")

            # Handle the case where image_file is None
            if image_file is None:
                # If no image is provided, store None in the user_profile_img field
                user.user_profile_img = None
            else:
                # Replace 'your_api_key' with your actual ImageBB API key
                api_key = "db34544520f57ff0f15d2b1ece2794b3"
                print("Image received")

                # Upload the image to ImageBB
                image_url = self.upload_to_imagebb(api_key, image_file.read())
                print("Image Url", image_url)

                if image_url:
                    # Update the user's profile image URL in the database
                    user.user_profile_img = image_url
                else:
                    return Response({
                    'success': False,
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': 'Failed to upload image',
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

        # Save the user object after processing the image (or lack thereof)
        user.save()
        
        return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': "DP updated successfully",
                }, status=status.HTTP_200_OK) 
