from rest_framework import serializers
from .models import CustomUser, OTP, UserProfile 
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from payment.models import Subscription
User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role']
        read_only_fields = ['id', 'is_active', 'is_staff', 'is_superuser']
        
        
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'role']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )
        UserProfile.objects.create(
            user=user,
        )
        Subscription.objects.create(user=user)
        return user

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['id', 'email', 'otp', 'created_at', 'attempts']
        read_only_fields = ['id', 'created_at', 'attempts']

class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'name', 'phone_number', 'address', 'joined_date']
        read_only_fields = ['id', 'joined_date']



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
   

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
      

        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials")

   

        return user