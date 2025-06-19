from datetime import datetime, time
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from . import serializers
from django.db.models import Q
from . import models
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from . import utils
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# global pagination
paginate = PageNumberPagination()
paginate.page_size = 10

# user register
@swagger_auto_schema(
        method='POST',
        operation_id='user register',
        operation_description="POST API for user registration through email and password",
        request_body=serializers.UserSerializer,
        responses={
            201: 'User is registered successfully',
            400: 'User exists by username/email or validation error'
        })
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):

    url = request.get_full_path()

    payload = request.data
    user_request = serializers.UserSerializer(data=payload)

    user = utils.check_user_exists(
            payload['username'],
            payload['email'])
        
    if user is not None:
        err = serializers.ResponseSerializer({
            'message':'Another user exists with same username/email',
            'status':400,
            'url':url})
        return Response(err.data,status=400)

    if user_request.is_valid():
        user = user_request.save()
        user.set_password(user_request.validated_data['password'])
        user.save()
        
        res = serializers.ResponseSerializer({
            'message':'Congratulations! You have registered successfully',
            'status':201,
            'url':url})
        return Response(res.data, status=201)
    
    err = serializers.ResponseSerializer({
            'message':'validation failed on request body',
            'url':url,
            'status':400})
    return Response(err.data, status=400)

# create doctor
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
@permission_classes([IsAuthenticated])
def create_doctor(request):

    url = request.get_full_path()

    payload = request.data
    
    doctor_request = serializers.DoctorSerializer(data=payload)

    if doctor_request.is_valid():

        user = utils.check_user_by_username(request.user)
        
        if user is None:
            err = serializers.ResponseSerializer({
                'message':'User profile is not available with this username',
                'status':404,
                'url':url})
            return Response(err.data, status=400)
        
        models.Doctor.objects.create(
            user = user,
            **doctor_request.validated_data)
        
        res = serializers.ResponseSerializer({
            'message':'doctor profile is saved successfully',
            'status':201,
            'url':url})
        return Response(res.data, status=201)
    else:
        err = serializers.ResponseSerializer({
            'message':'something went wrong while saving doctor profile',
            'status':400,
            'url':url})
        return Response(err.data, status=400)

# get list of doctors
@swagger_auto_schema(
        method='GET',
        operation_id='get doctor list',
        operation_description='get list of doctors with filter and pagination feature',
        manual_parameters=[
            openapi.Parameter(
                name='page', 
                required=True, 
                in_=openapi.IN_QUERY, 
                type=openapi.TYPE_NUMBER),
            openapi.Parameter(
                name='sortby', 
                in_=openapi.IN_QUERY, 
                type=openapi.TYPE_STRING),
            openapi.Parameter(
                name='sortorder', 
                in_=openapi.IN_QUERY, 
                type=openapi.TYPE_STRING),
            openapi.Parameter(
                name='specialization',
                required=False, 
                in_=openapi.IN_QUERY, 
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='start_time',
                required=False, 
                in_=openapi.IN_QUERY, 
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='end_time',
                required=False, 
                in_=openapi.IN_QUERY, 
                type=openapi.TYPE_STRING
            )])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_list(request):
    
    url = request.get_full_path()

    spec_value = request.query_params.get('specialization')
    start_val = request.query_params.get('start_time')
    end_val = request.query_params.get('end_time')
    sortby = request.query_params.get('sortby')
    sortorder = request.query_params.get('sortorder')

    doctors = models.Doctor.objects.all()

    if spec_value:
        doctors = doctors.filter(specialization = spec_value)

    if start_val:
        start_time = time.fromisoformat(start_val)
        doctors = doctors.filter(start_time__lte = start_time)

    if end_val:
        end_time = time.fromisoformat(end_val)
        doctors = doctors.filter(end_time__gte = end_time)

    if sortby and sortorder:
        if not sortby in ['specialization', 'start_time', 'end_time', 'first_name', 'last_name', "created_at"]:
            err = serializers.ResponseSerializer({
                'message':'please provide a valid sortby option',
                'status':400,
                'url':url})
            return Response(err.data, status=400)
        
        sortby_val = sortby

        if sortby == 'first_name' or sortby == 'last_name':
            sortby_val = f"user__{sortby}"
        
        if sortorder == 'desc':
            sortby_val = f"-{sortby_val}"
        doctors = doctors.order_by(sortby_val)

    pagedate = paginate.paginate_queryset(doctors, request)

    res = serializers.DoctorGetSerializer(pagedate, many=True)
    return Response(res.data, status=200)

# create patient
@swagger_auto_schema(
        method='POST',
        operation_id='create patient',
        operation_description='create patient record with provided details - gender, dob and phone number',
        request_body=serializers.PatientSerializer,
        responses={
            201: 'created patient record successfully',
            400: 'validation failed on request body'
        })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_patient(request):

    url = request.get_full_path()

    payload = request.data
    patient_request = serializers.PatientSerializer(data=payload)
    if patient_request.is_valid():

        user = utils.check_user_by_username(request.user)
        
        if user is None:
            err = serializers.ResponseSerializer({
                'message':'User profile is not available with given username',
                'status':404,
                'url':url})
            return Response(err.data, status=400)
        
        models.Patient.objects.create(
            user = user,
            **patient_request.validated_data)
        
        res = serializers.ResponseSerializer({
                'message':'Patient profile is saved successfully',
                'status':201,
                'url':url})
        return Response(res.data, status=201)
    else:
        err = serializers.ResponseSerializer({
                'message':'Something went wrong while saving patient profile',
                'status':400,
                'url':url})
        return Response(err.data, status=400)

# update doctor
@swagger_auto_schema(
        method='PATCH',
        operation_id='update doctor',
        operation_description='update doctor details with provided information',
        request_body=serializers.DoctorSerializer,
        manual_parameters=[
            openapi.Parameter(
                name='doctor_id',
                in_=openapi.IN_PATH,
                description='primary key of doctor record',
                type=openapi.TYPE_NUMBER
        )])
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_doctor(request, doctor_id):
    url = request.get_full_path()

    doctor = utils.check_doctor_exists(doctor_id)
    if doctor is None:
            err = serializers.ResponseSerializer({
                'message':'doctor does\'nt exists by provided doctor_id',
                'status':404,
                'url':url})
            return Response(err.data, status=404)
    doc_request = serializers.DoctorSerializer(data=request.data)
    if doc_request.is_valid():
        doctor.available_days = doc_request.validated_data['available_days']
        doctor.start_time = doc_request.validated_data['start_time']
        doctor.end_time = doc_request.validated_data['end_time']
        doctor.specialization = doc_request.validated_data['specialization']
        doctor.save()

        res = serializers.ResponseSerializer({
                'message':'doctor profile is updated successfully',
                'status':200,
                'url':url})
        return Response(res.data, status=200)
    
    err = serializers.ResponseSerializer({
                'message':'something went wrong while updating doctor details',
                'status':400,
                'url':url})            
    return Response(err.data, status=400)

# delete doctor
@swagger_auto_schema(
        method='DELETE',
        operation_id='delete doctor',
        operation_description='delete doctor\'s record using p.k',
        manual_parameters=[
            openapi.Parameter(name='doctor_id', in_=openapi.IN_PATH, type=openapi.TYPE_NUMBER)
        ],
        responses={
            200: 'record deleted successfully',
            404: 'record not found by p.k'
        })
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_doctor(request, doctor_id):
    url = request.get_full_path()

    doctor = utils.check_doctor_exists(doctor_id)
    if doctor is None:
            err = serializers.ResponseSerializer({
                'message':'doctor does\'nt exists by provided doctor_id',
                'status':404,
                'url':url})
            return Response(err.data, status=404)
    doctor.user.delete()
    res = serializers.ResponseSerializer({
                'message':'doctor\'s record deleted successfully',
                'status':200,
                'url':url})
    return Response(res.data, status=200)

# update patient
@swagger_auto_schema(
        method='PATCH',
        operation_id='update patient',
        operation_description='update patient details with provided information',
        request_body=serializers.PatientSerializer,
        manual_parameters=[
            openapi.Parameter(
                name='patient_id',
                in_=openapi.IN_PATH,
                description='primary key of doctor record',
                type=openapi.TYPE_NUMBER
        )])
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_patient(request, patient_id):
    url = request.get_full_path()
    patient = utils.check_patient_exists(patient_id)
    if patient is None:
            err = serializers.ResponseSerializer({
                'message':'patient does\'nt exists by provided patient_id',
                'url':url,
                'status':404
            })
            return Response(err.data, status=404)
    patient_request = serializers.PatientSerializer(data=request.data)
    if patient_request.is_valid():
        patient.dob = patient_request.validated_data['dob']
        patient.gender = patient_request.validated_data['gender']
        patient.phone_number = patient_request.validated_data['phone_number']
        patient.save()    

        res = serializers.ResponseSerializer({
                'message':'patient record is updated successfully',
                'url':url,
                'status':200
            })
        return Response(res.data, status=200)
    err = serializers.ResponseSerializer({
                'message':'validation failed in request body',
                'url':url,
                'status':400
            })   
    return Response(err.data, status=400)

# delete patient
@swagger_auto_schema(
        method='DELETE',
        operation_id='delete patient',
        operation_description='delete patient\'s record using p.k',
        manual_parameters=[
            openapi.Parameter(name='patient_id', in_=openapi.IN_PATH, type=openapi.TYPE_NUMBER)
        ],
        responses={
            200: 'record deleted successfully',
            404: 'record not found by p.k'
        })
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_patient(request, patient_id):
    url = request.get_full_path()
    patient = utils.check_patient_exists(patient_id)
    if patient is None:
            err = serializers.ResponseSerializer({
                'message':'patient record does\'nt exists by provided p.k',
                'status':404,
                'url':url
            })
            return Response(err.data, status=404)
    patient.user.delete()
    res = serializers.ResponseSerializer({
                'message':'patient record is deleted successfully',
                'status':200,
                'url':url
            })
    return Response(res.data, status=200)

# create doctor availability
@swagger_auto_schema(
        method='POST',
        operation_id='create doctor availability',
        operation_description='create doctor availability with date, start-time and end-time',
        request_body=serializers.DoctorAvailabilitySerializer,
        responses={
            201: 'created doctor availability record successfully',
            400: 'validation failed on request body'
        })
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_doctor_availability(request):
    url = request.get_full_path()

    doc_id = int(request.query_params['doctor_id'])
    doctor = utils.check_doctor_exists(doc_id)

    if doctor is None:
        err = serializers.ResponseSerializer({
            'message':'doctor does\'nt exists by provided p.k',
            'status':404,
            'url':url
        })
        return Response(err.data, status=404)
    
    payload = serializers.DoctorAvailabilitySerializer(data=request.data)
    if payload.is_valid():

        models.DoctorAvailability.objects.create(
            doctor = doctor,
            date = payload.validated_data['date'],
            start_time = payload.validated_data['start_time'],
            end_time = payload.validated_data['end_time'])
        res = serializers.ResponseSerializer({
            'message':'Time slot for doctor availability is created successfully',
            'status':201,
            'url':url
        })
        return Response(res.data, status=201)
    return Response({'error': 'something went wrong!'}, status=400)

# create doctor availability in bulk
@swagger_auto_schema(
        method='POST',
        operation_id='create doctor availability bulk',
        operation_description='create doctor availability in bulk using excel template',
        # manual_parameters=[openapi],
        # request_body=serializers.DoctorAvailabilitySerializer,
        responses={
            201: 'created doctor availability record successfully',
            400: 'validation failed on request body'
        })
@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAdminUser])
def create_doctor_availability_bulk(request):
    url = request.get_full_path()
    file = request.FILES['upload_file']
    is_valid, error_msg = utils.validate_file(file)
    if not is_valid:
        err = serializers.ResponseSerializer({
            'message':error_msg,
            'status':400,
            'url':url
        })
        return Response(err.data, status=400)
    
    data_list, error_list = utils.process_docavailability_bulkupload(file)

    if error_list is not None:
        err = serializers.BulkErrorSerializer({
            'message':error_msg,
            'status':400,
            'url':url,
            'data': error_list
        })
        return Response(err.data,status=400)
    
    error_list = []
    for data in data_list:
        is_created = utils.create_individual_slot(data)
        if not is_created:
            error_list.append(f'doctor \"{data.get('doc_username')}\" does not exists')
    if error_list:
        err = serializers.BulkErrorSerializer({
            'message': 'Error occurred while uploading data in bulk',
            'status':400,
            'url':url,
            'data': error_list
        })
        return Response(err.data,status=400)

    res = serializers.ResponseSerializer({
            'message':'Data for doctor availability is uploaded successfully',
            'status':201,
            'url':url
        })
    return Response(res.data,status=201)

# create appointment
@swagger_auto_schema(
        method='POST',
        operation_id='book appointment',
        operation_description='book appointment with doctor at given date and time',
        request_body=serializers.AppointmentSerializer,
        manual_parameters=[openapi.Parameter(name='doctor_id', in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER, required=True)],
        responses={
            201: 'booked appointment with doctor successfully',
            400: 'validation failed on request body'
        })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    url = request.get_full_path()

    doc_id = int(request.query_params['doctor_id'])

    doctor = utils.check_doctor_exists(doc_id)
    patient = utils.check_patient_by_username(request.user)
    if doctor is None:
        err = serializers.ResponseSerializer({
            'message':'Doctor\'s record not found by provided p.k',
            'status':404,
            'url':url
        })
        return Response(err.data,status=404)
    
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
            err = serializers.ResponseSerializer({
                'message':'Time slot is not available for the appointment',
                'status':404,
                'url':url})
            return Response(err.data,status=404)
        
        appointment_exists = models.Appointment.objects.filter(
            Q(doctor = doctor) &
            Q(patient = patient) &
            Q(date = date) &
            Q(status = models.AppointmentStatus.BOOKED)).exists()
        
        if appointment_exists:
            err = serializers.ResponseSerializer({
                'message':'Appointment is already booked with the selected doctor at given date and time',
                'status':400,
                'url':url})
            return Response(err.data,status=400)

        models.Appointment.objects.create(
            doctor = doctor,
            patient = patient,
            date = date,
            time = time)
        
        res = serializers.ResponseSerializer({
            'message':'Appointment with doctor is booked successfully',
            'status':201,
            'url':url
        })
        return Response(res.data,status=201)

    err = serializers.ResponseSerializer({
            'message':'Validation failed on request body',
            'status':400,
            'url':url
        })
    return Response(err.data,status=400)
    

# get list of patients
@swagger_auto_schema(
        method='GET',
        operation_id='get patient list',
        operation_description='get list of patients with filter, sorting and pagination features',
        manual_parameters=[
            openapi.Parameter(name='gender', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, default='M'),
            openapi.Parameter(name='min_dob', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter(name= 'max_dob', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter(name='search', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter(name='sortby', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, default='created_at'),
            openapi.Parameter(name='sortorder', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, default='desc')
        ])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_list(request):
    url = request.get_full_path()

    gen_val = request.query_params.get('gender')
    min_dob_val = request.query_params.get('min_dob')
    max_dob_val = request.query_params.get('max_dob')
    search_val = request.query_params.get('search')
    sortby_val = request.query_params.get('sortby')
    sortorder_val = request.query_params.get('sortorder')

    patients = models.Patient.objects.all()

    if gen_val:
        patients = patients.filter(gender = gen_val)
    if min_dob_val and max_dob_val:
        try:
            min_dob = datetime.strptime(min_dob_val, '%d-%m-%Y')
            max_dob = datetime.strptime(max_dob_val, '%d-%m-%Y')
            patients = patients.filter(Q(dob__gte = min_dob) & Q(dob__lte = max_dob))
        except ValueError:
            err = serializers.ResponseSerializer({
                'message':'Unable to parse min_dob/max_dob. Please provide the dates in proper format',
                'status':400,
                'url':url
            })
            return Response(err.data,status=400)
    if search_val:
        patients = patients.filter(
            Q(user__first_name__icontains = search_val) |
            Q(user__last_name__icontains = search_val) |
            Q(user__username__icontains = search_val))
    if sortby_val and sortorder_val:
        if not sortby_val in ['first_name', 'last_name', 'dob', 'gender', 'created_at']:
            err = serializers.ResponseSerializer({
                'message':'Invalid sortby value. Please try again.',
                'status':400,
                'url':url})
            return Response(err.data,status=400)
        
        sortby = sortby_val
        if sortby == 'first_name' or sortby == 'last_name':
            sortby = f"user__{sortby}"
        if sortorder_val == 'desc':
            sortby = f"-{sortby}"
        patients.order_by(sortby)
    
    pagedata = paginate.paginate_queryset(patients, request)
    res = serializers.PatientGetSerializer(pagedata, many=True)
    return Response(res.data, status=200)

# get list of appointments
@swagger_auto_schema(
        method='GET',
        operation_id='get appointments list',
        operation_description='get list of appointments with filter, sorting and pagination features',
        manual_parameters=[
            openapi.Parameter(name='specialization', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter(name='doctor', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter(name='min_date', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter(name='max_date', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter(name='sortby', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, default='created_at'),
            openapi.Parameter(name='sortorder', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, default='desc')
        ])
@api_view(['GET'])
def get_appointments_of_patient(request):

    url = request.get_full_path()

    spec_val = request.query_params.get('specialization')
    doc_val = request.query_params.get('doctor') # doctor username
    status_val = request.query_params.get('status_val')
    min_date_val = request.query_params.get('min_date')
    max_date_val = request.query_params.get('max_date')
    sortby_val = request.query_params.get('sortby')
    sortorder_val = request.query_params.get('sortorder')

    patient = utils.check_patient_by_username(request.user)
    if patient is None:
        err = serializers.ResponseSerializer({
            'message':'Patient\'s record not found by provided p.k',
            'status':404,
            'url':url
        })
        return Response(err.data,status=404)

    appointments = models.Appointment.objects.filter(patient = patient)

    if spec_val:
        appointments = appointments.filter(doctor__specialization = spec_val)
    if doc_val:
        appointments = appointments.filter(doctor__user__username = doc_val)
    if status_val:
        appointments = appointments.filter(status = status_val)
    if min_date_val and max_date_val:
        try:
            min_date = datetime.strptime(min_date_val, '%d-%m-%Y')
            max_date = datetime.strptime(max_date_val, '%d-%m-%Y')
            patients = patients.filter(Q(date__gte = min_date) & Q(date__lte = max_date))
        except ValueError:
            err = serializers.ResponseSerializer({
                'message':'Unable to parse min_date/max_date. Please provide the dates in proper format',
                'status':400,
                'url':url})
            return Response(err.data,status=400)
    if sortby_val and sortorder_val:
        if not sortby_val in ['date', 'status', 'doctor_username', 'patient_username', 'created_at']:
            err = serializers.ResponseSerializer({
                'message':'Invalid sortby option. Please try again',
                'status':400,
                'url':url})
            return Response(err.data,status=400)
        
        sortby = sortby_val
        if sortby_val == 'doctor_username':
            sortby = f'doctor__user__username'
        elif sortby_val == 'patient_username':
            sortby = f'patient__user__username'
        if sortorder_val == 'desc':
            sortby = f'-{sortby}'
        appointments = appointments.order_by(sortby)

    pagedata = paginate.paginate_queryset(appointments, request)
    res = serializers.AppointmentGetSerializer(pagedata, many=True)
    return Response(res.data, status=200)

@swagger_auto_schema
@api_view(['POST'])
def create_prescription(request, appointment_id):
    url = request.get_full_path()

    payload = request.data
    prescription_request = serializers.PrescriptionSerializer(data=payload)
    if prescription_request.is_valid():
        appointment = models.Appointment.objects.filter(appointment_id = appointment_id).first()
        if appointment is None:
            err = serializers.ResponseSerializer({
                'message':'Appointment not found by provided appointment_id',
                'status':404,
                'url':url})
            return Response(err.data, status=404)
        
        models.Prescription.objects.create(
            appointment = appointment,
            **prescription_request.validated_data)
        res = serializers.ResponseSerializer({
            'message':'prescription added successfully in the appointment',
            'status':201,
            'url':url
        })
        return Response(res.data,status=201)
    err = serializers.ResponseSerializer({
            'message':'Validation failed on request body.',
            'status':400,
            'url':url})
    return Response(err.data, status=400)