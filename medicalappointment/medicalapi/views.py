from rest_framework.decorators import api_view, parser_classes, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from . import serializers
from django.db.models import Q
from . import models
from rest_framework.parsers import MultiPartParser
from . import utils
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(
        method='POST',
        operation_id='register user',
        operation_description="register user in the application using first_name, last_name, username, email and password",
        request_body=serializers.UserSerializer,
        responses={
            201: 'User is registered successfully',
            400: 'User exists by username/email or validation error'
        })
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    POST API for registering user to the application, either you are doctor/patient
    """
    payload = request.data
    user_request = serializers.UserSerializer(data=payload)

    user = utils.check_user_exists(
            payload['username'],
            payload['email'])
        
    if user is not None:
        return Response({
            'message': 'Another user exists with same username/email'}, 
            status=400)

    if user_request.is_valid():
        user = user_request.save()
        user.set_password(user_request.validated_data['password'])
        user.save()

        return Response({'message': 'user is registered successfully'}, status=201)

@swagger_auto_schema(
        method='POST',
        operation_id='create doctor profile',
        operation_description="create doctor profile on the basis of existing user. Specialization, available days, start time and end time are required.",
        request_body=serializers.DoctorSerializer,
        responses={
            201: 'Doctor profile is created successfully',
            400: 'User does not exists by username or validation error'
        })
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def create_doctor(request):
    """
    POST API to create doctor record
    """
    payload = request.data
    
    doctor_request = serializers.DoctorSerializer(data=payload)

    if doctor_request.is_valid():

        user = utils.check_user_by_username(request.user)
        
        if user is None:
            return Response({
                'message': 'User profile is not available with this username'}, 
                status=400)
        
        models.Doctor.objects.create(
            user = user,
            **doctor_request.validated_data)
        
        # doctor_request.save()

        return Response(doctor_request.data, status=201)
    else:
        return Response({'message': 'something went wrong!'}, status=400)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def create_patient(request):
    payload = request.data
    patient_request = serializers.PatientSerializer(data=payload)
    if patient_request.is_valid():

        user = utils.check_user_by_username(request.user)
        
        if user is not None:
            return Response({
                'message': 'User profile is not available with given username'}, 
                status=400)
        
        patient_request.save()

        return Response(patient_request.data, status=201)
    else:
        return Response({'message': 'something went wrong!'}, status=400)

@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
def update_doctor(request, doctor_id):
    doctor = utils.check_doctor_exists(doctor_id)
    if doctor is None:
            return Response({
                'error': 'doctor does\'nt exists by provided doctor_id'}, status=404)
    # if request.method == 'PATCH':
    doc_request = serializers.DoctorSerializer(data=request.data)
    if doc_request.is_valid():
        doctor.available_days = doc_request.validated_data['available_days']
        doctor.start_time = doc_request.validated_data['start_time']
        doctor.end_time = doc_request.validated_data['end_time']
        doctor.specialization = doc_request.validated_data['specialization']
        doctor.save()

        return Response(doc_request.data, status=200)            
    return Response({'error': 'something went wrong!'}, status=400)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def delete_doctor(request, doctor_id):
    doctor = utils.check_doctor_exists(doctor_id)
    if doctor is None:
            return Response({
                'error': 'doctor does\'nt exists by provided doctor_id'}, status=404)
    doctor.user.delete()
    return Response({'message': 'doctor\'s record deleted successfully'}, status=200)

@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
def update_patient(request, patient_id):
    patient = utils.check_patient_exists(patient_id)
    if patient is None:
            return Response({
                'error': 'patient does\'nt exists by provided patient_id'}, status=404)
    patient_request = serializers.PatientSerializer(data=request.data)
    if patient_request.is_valid():
        patient.dob = patient_request.validated_data['dob']
        patient.gender = patient_request.validated_data['gender']
        patient.phone_number = patient_request.validated_data['phone_number']
        patient.save()    
        return Response(patient_request.data, status=200)   
    return Response({'error': 'something went wrong!'}, status=400)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def delete_patient(request, patient_id):
    patient = utils.check_patient_exists(patient_id)
    if patient is None:
            return Response({
                'error': 'patient does\'nt exists by provided patient_id'}, status=404)
    patient.user.delete()
    return Response({'message': 'patient\'s record deleted successfully'}, status=200)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def create_doctor_availability(request):
    doc_id = int(request.query_params['doctor_id'])
    doctor = utils.check_doctor_exists(doc_id)

    if doctor is None:
        return Response({
                'error': 'doctor does\'nt exists by provided doctor_id'}, status=404)
    
    payload = serializers.DoctorAvailabilitySerializer(data=request.data)
    if payload.is_valid():

        models.DoctorAvailability.objects.create(
            doctor = doctor,
            date = payload.validated_data['date'],
            start_time = payload.validated_data['start_time'],
            end_time = payload.validated_data['end_time'])
        
        return Response({
            'message':'Time slot for doctor availability is created successfully'}, 
            status=201)
    return Response({'error': 'something went wrong!'}, status=400)

@api_view(['POST'])
@parser_classes([MultiPartParser])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def create_doctor_availability_bulk(request):
    file = request.FILES['upload_file']
    is_valid, error_msg = utils.validate_file(file)
    if not is_valid:
        return Response({'error': error_msg}, status=400)
    
    data_list, error_list = utils.process_docavailability_bulkupload(file)

    if error_list is not None:
        return Response({
            'error': 'validation failed for excel upload', 
            'details': error_list},
            status=400)
    
    error_list = []
    for data in data_list:
        is_created = utils.create_individual_slot(data)
        if not is_created:
            error_list.append(f'doctor \"{data.get('doc_username')}\" does not exists')
    if error_list:
        return Response({'error': error_list}, status=400)

    return Response({'message':'Bulk upload of doctor availability is done successfully'}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    """
    POST API to book an appointment with the doctor at given date time
    1. check whether doctor and patient exists in db or not
    2. check the doctor availability, if not available reject the request.
    3. if all parameter are ok, then book appointment
    """
    doc_id = int(request.query_params['doctor_id'])
    pat_id = request.query_params['patient_id']

    doctor = utils.check_doctor_exists(doc_id)
    patient = utils.check_patient_exists(pat_id)
    if doctor is None:
        return Response({
                'error': 'doctor does\'nt exists by provided doctor_id'}, status=404)
    
    if patient is None:
        return Response({
                'error': 'patient does\'nt exists by provided patient_id'}, status=404)
    
    payload = serializers.AppointmentSerializer(data=request.data)
    if payload.is_valid():
        date = payload.validated_data['date']
        time = payload.validated_data['time']
        slot = models.DoctorAvailability.objects.filter(
            Q(doctor = doctor) &
            Q(start_time__lte = time) &
            Q(end_time__gte = time) &
            Q(is_available = True)).exists()
        
        if not slot:
            return Response({
                'error': 'doctor is not available at given date and time'}, status=404)
        
        appointment_exists = models.Appointment.objects.filter(
            Q(doctor = doctor) &
            Q(patient = patient) &
            Q(date = date) &
            Q(status = models.AppointmentStatus.BOOKED)).exists()
        
        if appointment_exists:
            return Response({
                'error': 'Already an appointment is booked with same doctor on given date'}, 
                status=400)

        models.Appointment.objects.create(
            doctor = doctor,
            patient = patient,
            date = date,
            time = time)
        
        return Response({
                'message': 'Your appointment with doctor is booked successfully'}, 
                status=201)