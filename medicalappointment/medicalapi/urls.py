from django.urls import path, include
from . import views

urlpatterns = [
    # register endpoint
    path('auth/register', views.register_user, name='register_user'),

    # doctor's endpoint
    path('doctors/', include('medicalapi.doctorurls')),
    # path('doctors', views.create_doctor, name='create_doctor'),
    # path('doctors/list', views.get_doctor_list, name='doctor_list'),
    # path('doctors/id/<int:doctor_id>', views.update_doctor, name='update_doctor'),
    # path('doctors/id/<int:doctor_id>/delete', views.delete_doctor, name='delete_doctor'),

    # patient's endpoint
    path('patients', views.create_patient, name='create_patient'),
    path('patients/list', views.get_patient_list, name='patient_list'),
    path('patients/id/<int:patient_id>', views.update_patient, name='update_patient'),
    path('patients/id/<int:patient_id>', views.delete_patient, name='delete_patient'),

    # availability endpoint
    path('slots', views.create_doctor_availability, name = 'create_doctor_availability'),
    path('slots/bulk-upload', views.create_doctor_availability_bulk, name = 'create_slots_bulk'),

    # appointment endpoint
    path('appointments', views.create_appointment, name='create_appointment'),
    path('appointments/list', views.get_appointments_of_patient, name='patient_appointments')

    # prescription endpoint
    # path('prescriptions/<int:appointment_id>')
]