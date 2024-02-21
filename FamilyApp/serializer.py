from rest_framework import serializers
from FamilyApp.models import FamilyMember,Relationship
from django import forms
import datetime
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = FamilyMember
        fields = ['full_name', 'email', 'phone_no','date_of_birth','password', 'password2']
        extra_kwargs = {
            'password':{'write_only':True}
        }

    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        email = (attrs.get('email')).lower()
        print('Email-From-Validation:', email)
        #validate password and confirm password is same
        if FamilyMember.objects.filter(email=email).exists():
            raise forms.ValidationError(f"{email} with this email already exists.")
        #validate password and confirm password is same
        if(password != password2):
            raise serializers.ValidationError("Confirm password not match with password!")

        return attrs
    
    def create(self, validated_data):
        return FamilyMember.objects.create_user(**validated_data)
    

class UserLoginSerializer(serializers.ModelSerializer):
        phone_no = serializers.CharField(max_length=20)
        class Meta:
            model = FamilyMember
            fields = ['phone_no', 'password',]

        def validate(self, data):
            phone_no = data.get('phone_no')
            password = data.get('password')

            user = authenticate(phone_no=phone_no, password=password)

            if user is not None:
                if not user.is_active:
                    raise AuthenticationFailed('Account disabled, contact with Manager')

                # Update last_login time for the user
                user.last_login = timezone.now()
                user.save()

                # Return both the authenticated user and validated data
                return {'user': user, 'data': data}
            else:
                raise AuthenticationFailed(f'Invalid credentials, try again or Account disabled')
            

class UserProfileEditSerializer(serializers.ModelSerializer):
     class Meta:
          model = FamilyMember
          exclude = ['is_staff', 'is_active', 'is_superuser']


class UserProfileSerializer(serializers.ModelSerializer):
     class Meta:
          model = FamilyMember
          exclude = ['password']

# class UserChangePasswordSerializer(serializers.Serializer):
#     password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
#     password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
     
#     class Meta:
#             fields = ['password', 'password2']
#     def validate(self, attrs):
#         password = attrs.get('password')
#         password2 = attrs.get('password2')

#         user = self.context.get('user')

#         if(password != password2):
#             raise serializers.ValidationError("Confirm password not match with password!")
        

#         user.set_password(password)
#         user.save()
#         return attrs



class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
     
    class Meta:
            fields = ['password', 'password2']
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        user = self.context.get('user')

        if(password != password2):
            
            raise serializers.ValidationError("Confirm password not match with password!")
        

        user.set_password(password)
        user.save()
        return attrs
    

class CreateConnectionSerializer(serializers.ModelSerializer):
    # related_person = serializers.PrimaryKeyRelatedField(queryset=FamilyMember.objects.all())

    class Meta:
        model = Relationship
        fields = ['related_person', 'relationship_type']

    def validate_related_person(self, value):
        user = self.context['request'].user
        if value == user:
            raise serializers.ValidationError("You cannot create a relationship with yourself.")
        
        existing_connections = Relationship.objects.filter(person=user, related_person=value)
        if existing_connections.exists():
            raise serializers.ValidationError("Connection already exists with this person.")
        

        return value
        
        

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['person'] = user
        return super().create(validated_data)
    

class RelatedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        exclude = ['password']
    
class ConnectionSerializer(serializers.ModelSerializer):
    related_person_details = RelatedPersonSerializer(source='related_person', read_only=True)

    class Meta:
        model = Relationship
        fields = ['id','relationship_type','related_person_details']

class FamilyMemberSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        exclude = ['password']