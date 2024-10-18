from rest_framework import serializers
from .models import Business, Service, Customer, Appointment, Schedule, CustomUser
from django.contrib.auth import authenticate

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'address', 'phone']

class ServiceSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'duration', 'price']

    def get_duration(self, obj):
        hours, remainder = divmod(obj.duration.seconds, 3600)
        minutes = remainder // 60
        return f"{hours}h {minutes:02d}min"

    def get_price(self, obj):
        return f"IQD {obj.price}"

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone', 'date_of_birth']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'customer', 'service', 'staff', 'start_time', 'end_time', 'status']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'staff', 'date', 'start_time', 'end_time']

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type', 'business']
        read_only_fields = ['user_type', 'business']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'user_type', 'business']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data['user_type'],
            business=validated_data.get('business')
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")