from django.urls import path
from . import views

urlpatterns = [
    # doctor's endpoint
    path('doctors', views.create_doctor, name='create_doctor'),
    path('doctors/<int:doctor_id>', views.update_doctor, name='update_doctor'),

    # patient's endpoint
    path('patients', views.create_patient, name='create_patient'),
    path('patients/<int:patient_id>', views.update_patient, name='update_patient'),

    # availability endpoint
    path('slots', views.create_doctor_availability, name = 'create_doctor_availability'),
    path('slots/bulk-upload', views.create_slots_bulk, name = 'create_slots_bulk'),

    # appointment endpoint
    path('appointments', views.create_appointment, name='create_appointment'),
    # path('appointments/<int:appointment_id>', views.create) update appointment
]