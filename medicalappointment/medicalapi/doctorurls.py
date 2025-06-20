from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_doctor, name='create_doctor'),
    path('list', views.get_doctor_list, name='doctor_list'),
    path('id/<int:doctor_id>', views.update_doctor, name='update_doctor'),
    path('id/<int:doctor_id>/delete', views.delete_doctor, name='delete_doctor'),
]