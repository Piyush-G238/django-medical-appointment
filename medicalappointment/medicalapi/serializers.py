from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Clinic

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]

class DoctorSerializer(serializers.Serializer):
    specialization = serializers.CharField(max_length=100)
    available_days = serializers.CharField(max_length=100)
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = "__all__"

class DoctorGetSerializer(DoctorSerializer):
    user = UserGetSerializer()
    clinic = ClinicSerializer()
    created_at = serializers.DateTimeField()

class PatientSerializer(serializers.Serializer):
    dob = serializers.DateField(format='%d-%m-%Y',input_formats=['%d-%m-%Y'])
    gender = serializers.CharField(allow_null=True)
    phone_number = serializers.CharField(max_length = 12)

class PatientGetSerializer(PatientSerializer):
    user = UserGetSerializer()

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

class AppointmentGetSerializer(AppointmentSerializer):
    doctor = DoctorGetSerializer()
    patient = PatientGetSerializer()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

class PrescriptionSerializer(serializers.Serializer):
    notes = serializers.CharField()
    medications = serializers.CharField()

class ResponseSerializer(serializers.Serializer):
    message=serializers.CharField()
    status=serializers.IntegerField()

class FieldErrorSerializer(ResponseSerializer):
    field = serializers.ListField()