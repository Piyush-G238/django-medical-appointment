from django.db import models
from django.contrib.auth.models import User

class Gender(models.TextChoices):
    MALE = 'M'
    FEMALE = 'F'
    TRANSGENDER = 'T'
    OTHER = 'O'

class AppointmentStatus(models.TextChoices):
    BOOKED = 'B'
    CANCELLED = 'C'

class TicketStatus(models.TextChoices):
    OPEN = 'O'
    CLOSED = 'C'

class Clinic(models.Model):
    class Meta:
        db_table = 'gen_clinic'
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)

# Create your models here.
class Doctor(models.Model):
    class Meta:
        db_table = 'gen_doctor'
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    available_days = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    doctor_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Patient(models.Model):
    class Meta:
        db_table ='gen_patient'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(db_column='date_of_birth')
    gender = models.CharField(
        choices=Gender, 
        default=Gender.MALE.value)
    phone_number = models.CharField(max_length=15)
    patient_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Appointment(models.Model):
    class Meta:
        db_table = 'gen_appointment'
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE)
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE)
    date = models.DateField(db_column='appointment_date')
    time = models.TimeField(db_column='appointment_time')
    status = models.CharField(
        choices=AppointmentStatus, 
        default=AppointmentStatus.BOOKED, 
        db_column='appointment_status')
    created_at = models.DateTimeField(auto_now_add=True)
    appointment_id = models.AutoField(primary_key=True)

class Prescription(models.Model):
    class Meta:
        db_table = 'gen_prescription'
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    notes = models.TextField()
    medications = models.TextField()
    issued_at = models.DateTimeField(auto_now_add=True)
    prescription_id = models.AutoField(primary_key=True)

class MedicalRecord(models.Model):
    class Meta:
        db_table = 'gen_medicalrecord'
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    treatment = models.TextField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now_add=True)
    medicalrecord_id = models.AutoField(primary_key=True)

class DoctorAvailability(models.Model):
    class Meta:
        db_table = 'gen_doctoravailability'
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

class SupportTicket(models.Model):
    class Meta:
        db_table = 'gen_supportticket'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(choices=TicketStatus, default=TicketStatus.OPEN.value)
    created_at = models.DateTimeField(auto_now_add=True)
