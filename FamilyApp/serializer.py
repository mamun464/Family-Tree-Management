from rest_framework import serializers
from FamilyApp.models import FamilyMember
from django import forms

class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = FamilyMember
        fields = ['full_name', 'email', 'phone_no','date_of_birth', 'is_alive','profession','current_address', 'permanent_address','password', 'password2']
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