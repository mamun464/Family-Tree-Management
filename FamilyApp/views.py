from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from FamilyApp.serializer import UserRegistrationSerializer ,UserLoginSerializer,UserProfileEditSerializer,UserProfileSerializer,UserChangePasswordSerializer,CreateConnectionSerializer,ConnectionSerializer,FamilyMemberSearchSerializer
from rest_framework.response import Response
from rest_framework import status
from FamilyApp.renderers import UserRenderer
from django.utils import timezone
from django.contrib.auth import authenticate,login
from FamilyApp.models import FamilyMember,Relationship
from rest_framework.permissions import IsAuthenticated,IsAdminUser
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
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
            error_messages = []
            for field, messages in errors.items():
                error_messages.append(f"{field}: {messages[0]}")  # Concatenate field name and error message
            return Response({
                "success": False,
                "status": 400,
                "message": "\n".join(error_messages)  # Join error messages with newline character
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

            user_serializer = UserProfileSerializer(user)
            user_data = user_serializer.data

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': f'Successfully logged in',
                'token':token,
                'user_data': user_data,
                },status=status.HTTP_200_OK)

        else:
            errors = serializer.errors
            error_messages = []
            for field, messages in errors.items():
                error_messages.append(f"{field}: {messages[0]}")  # Concatenate field name and error message
            return Response({
                "success": False,
                "status": 400,
                "message": "\n".join(error_messages)  # Join error messages with newline character
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
            print("---1--->>>>Image pack in foun from body")

            # Handle the case where image_file is None
            if image_file is None:
                # If no image is provided, store None in the user_profile_img field
                user.user_profile_img = None
                print("---2/A--->>>>Inside package No image found")
            else:
                # Replace 'your_api_key' with your actual ImageBB API key
                api_key = "db34544520f57ff0f15d2b1ece2794b3"
                print("Image received")

                # Upload the image to ImageBB
                image_url = self.upload_to_imagebb(api_key, image_file.read())
                print("---2--->>>>Image converted to url")
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
    

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        
        return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': f'Find updated profile',
                
                'user_data': serializer.data,
                },status=status.HTTP_200_OK)
        

class MemberProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    # print("-------------->>>>MemberProfileView Get Methods")
    def get(self, request):

        required_fields = ['user_id']

        for field in required_fields:
            if field not in request.query_params or not request.query_params[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)
               
        user_id = request.query_params.get('user_id',None)  # Retrieve user_id from query parameters
        if user_id is not None:
            user = FamilyMember.objects.filter(id=user_id).first()
            if user:
                serializer = FamilyMemberSearchSerializer(user)
                
                return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': 'Success',
                    'user_data': serializer.data,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': True,
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': 'No User found',
                    
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'user_id parameter is missing',
                    
                }, status=status.HTTP_400_BAD_REQUEST)

        
        
    

class UserEditView(APIView):
    
    # IsAuthenticated applited
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    # def get(self, request, format=None):
    #     serializer = UserProfileSerializer(request.user)
        
    #     return Response(serializer.data,status= status.HTTP_200_OK)

    def put(self,request):
        serializer = UserProfileEditSerializer(request.user)
        userData=serializer.data
        user_id = userData['id']
        try:
            user=FamilyMember.objects.get(pk=user_id)
        except FamilyMember.DoesNotExist:
             return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer=UserProfileEditSerializer(user,data=request.data,  partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': f'Profiles updated successfully',
                
                'user_data': serializer.data,
                },status=status.HTTP_200_OK)
        

        else:
            errors = serializer.errors
            error_messages = []
            for field, messages in errors.items():
                error_messages.append(f"{field}: {messages[0]}")  # Concatenate field name and error message
            return Response({
                "success": False,
                "status": 400,
                "message": "\n".join(error_messages)  # Join error messages with newline character
            }, status=status.HTTP_400_BAD_REQUEST)
        

class UserDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def delete(self, request):
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

        

        try:
            user.delete()
        except ProtectedError as e:
            return Response({
                    'success': False,
                    'status': status.HTTP_403_FORBIDDEN,
                    'message': f'User {user.full_name} cannot be deleted because they have data in other DB.',
                }, status=status.HTTP_403_FORBIDDEN) 

        return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': f'{user.full_name} deleted From Family',
                }, status=status.HTTP_200_OK) 
    

class UserPasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        required_fields = ['password', 'password2']

        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})

        try:
            print("before serializer test")
            serializer.is_valid(raise_exception=True)
            print("save hower age")
            # serializer.save()
            print("save hoye geche")
            return Response({
                'success': True, 
                'status': status.HTTP_200_OK, 
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            errors = serializer.errors
            error_messages = []
            for field, messages in errors.items():
                error_messages.append(f"{messages[0]}")

            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST, 
                'message': "\nxxxxxxxx".join(error_messages)
            }, status=status.HTTP_400_BAD_REQUEST)
        

class CreateConnectionView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        required_fields = ['related_person', 'relationship_type']

        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            related_person_id = int(request.data['related_person'])
            
        except ValueError:
            return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'Related Person ID May Not be Integer',
                }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            related_person=FamilyMember.objects.get(pk=related_person_id)
        except FamilyMember.DoesNotExist:
             return Response({
                    'success': False,
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Related Person is  Not Valid',
                }, status=status.HTTP_404_NOT_FOUND)

        try:
            user_id = request.user.id
            person = FamilyMember.objects.get(pk=user_id)
        except FamilyMember.DoesNotExist:
             return Response({
                    'success': False,
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Login User Not Valid',
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Instantiate the serializer with data and context
        serializer = CreateConnectionSerializer(data=request.data, context={'request': request})

        # Check if the data is valid
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'success': True, 
                    'status': status.HTTP_200_OK, 
                    'message': f'Connection established with {related_person.full_name}'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST, 
                    'message': f'Error occurred while saving connection: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Return response with validation errors
            errors = serializer.errors
            error_messages = []
            for field, messages in errors.items():
                error_messages.append(f"{messages[0]}")

            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST, 
                'message': "\n".join(error_messages)
            }, status=status.HTTP_400_BAD_REQUEST)
        

class RemoveConnectionView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def delete(self, request):
 
            connection_id = request.query_params.get('connection_id', None)

            if connection_id is None :
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST, 
                    'message': f'Connection ID are required in the request Params.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not connection_id.isdigit():
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST, 
                    'message': f" 'id' expected a number but got {connection_id}"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                connection_entry = Relationship.objects.get(id=connection_id)

            except Relationship.DoesNotExist:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST, 
                    'message': "Already Deleted Or Invalid Connection ID"
                }, status=status.HTTP_400_BAD_REQUEST)
            

            serializer = UserProfileEditSerializer(request.user)
            userData=serializer.data
            user_id = userData['id']
            if connection_entry.person.id != user_id:
                return Response({
                    'success': False,
                    'status': status.HTTP_403_FORBIDDEN, 
                    'message': f"Not Allowed! Connected Person is not you match with you."
                }, status=status.HTTP_403_FORBIDDEN)
            connection_entry.delete()

            return Response({
                    'success': True,
                    'status': status.HTTP_200_OK, 
                    'message': f"Connection is remove successfully with {connection_entry.related_person.full_name}"
                }, status=status.HTTP_200_OK)
                
class UserConnectionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            # Retrieve connections where the logged-in user appears as the person
            connections = Relationship.objects.filter(person=request.user)
            
            # Serialize the connections data
            serializer = ConnectionSerializer(connections, many=True)
            
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Connections retrieved successfully',
                'connected_person': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Failed to retrieve connections',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    

class FamilyMemberSearchAPIView(APIView):

    def post(self, request, format=None):

        query = request.query_params.get('query', None)

        if query is None  or query=="":
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST, 
                    'message': f'Please Enter Your Search Keyword'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Perform search using Django ORM
        results = FamilyMember.objects.filter(full_name__icontains=query) | \
                  FamilyMember.objects.filter(email__icontains=query) | \
                  FamilyMember.objects.filter(phone_no__icontains=query)

        # Serialize search results
        serializer = FamilyMemberSearchSerializer(results, many=True)

        return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': f'Your Search Results Found',
                
                'user_data': serializer.data,
                },status=status.HTTP_200_OK)

class AllMemberListView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        # Retrieve all active users
        active_users = FamilyMember.objects.filter(is_superuser=False)

        # Serialize the active users
        serializer = FamilyMemberSearchSerializer(active_users, many=True)

        # Return the serialized data in the response
        return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': f'All Family members',
                
                'user_data': serializer.data,
                },status=status.HTTP_200_OK)

class AncestorsView(APIView):
    def get_ancestors(self, person_id, ancestors=None, visited=None):
        if ancestors is None:
            ancestors = []
        if visited is None:
            visited = set()

        person = FamilyMember.objects.filter(id=person_id).first()
        if not person:
            return []

        visited.add(person.id)

        relationships = Relationship.objects.filter(person=person, relationship_type='Parent').all()

        for relationship in relationships:
            if relationship.related_person.id not in visited:
                ancestors.append(relationship.related_person)
                visited.add(relationship.related_person.id)
                self.get_ancestors(relationship.related_person.id, ancestors, visited)

        return ancestors

    def get(self, request):
        try:
            person_id = request.query_params.get('person_id', None)

            if person_id is None  or person_id=="":
                    return Response({
                        'success': False,
                        'status': status.HTTP_400_BAD_REQUEST, 
                        'message': f'Params is Missing'
                    }, status=status.HTTP_400_BAD_REQUEST)

            ancestors = self.get_ancestors(person_id)
            serializer = FamilyMemberSearchSerializer(ancestors, many=True)

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Ancestors Retrieved successfully',
                'ancestors': serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)