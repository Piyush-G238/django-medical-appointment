from django.urls import path
from . import views

urlpatterns = [
    # register endpoint
    path('auth/register', views.register_user, name='register_user'),

    # doctor's endpoint
    path('doctors', views.create_doctor, name='create_doctor'),
    path('doctors/list', views.get_doctor_list, name='doctor_list'),
    path('doctors/id/<int:doctor_id>', views.update_doctor, name='update_doctor'),
    path('doctors/id/<int:doctor_id>/delete', views.delete_doctor, name='delete_doctor'),

    # patient's endpoint
    path('patients', views.create_patient, name='create_patient'),
    path('patients/id/<int:patient_id>', views.update_patient, name='update_patient'),
    path('patients/id/<int:patient_id>', views.delete_patient, name='delete_patient'),

    # availability endpoint
    path('slots', views.create_doctor_availability, name = 'create_doctor_availability'),
    path('slots/bulk-upload', views.create_doctor_availability_bulk, name = 'create_slots_bulk'),

    # appointment endpoint
    path('appointments', views.create_appointment, name='create_appointment'),

    # prescription endpoint

    

]