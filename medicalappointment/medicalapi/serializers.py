from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Doctor, Patient, DoctorAvailability

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Doctor
        fields = ["user", "specialization", "available_days", "start_time", "end_time"]

    def create(self, validated_data):
        user_data = validated_data.pop('user')  # extract nested user data
        user = User.objects.create(**user_data)
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

class DoctorUpdateSerializer(serializers.Serializer):
    available_days = serializers.CharField(max_length=100)
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Patient
        fields = ["user", "dob", "gender", "phone_number"]
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')  # extract nested user data
        user = User.objects.create(**user_data)
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

class PatientUpdateSerializer(serializers.Serializer):
    dob = serializers.DateField(format='%d-%m-%Y')
    gender = serializers.CharField()
    phone_number = serializers.CharField(max_length = 12)

class DoctorAvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField(
        format='%d-%m-%Y', 
        input_formats=['%d-%m-%Y'])
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

class AppointmentSerializer(serializers.Serializer):
    date = serializers.DateField(
        format='%d-%m-%Y', 
        input_formats=['%d-%m-%Y'])
    time = serializers.TimeField(format='%H:%M')