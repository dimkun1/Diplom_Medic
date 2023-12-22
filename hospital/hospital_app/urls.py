from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('awards/', views.AwardsView.as_view(), name='awards'),

    path('patient_history_new/', views.PatientNewListView.as_view(), name='patient_history_new'),
    path('patient_history_old/', views.PatientOldListView.as_view(), name='patient_history_old'),
    path('patient_appointment_new/', views.PatientNewAppointmentView.as_view(), name='patient_appointment_new'),

    path('doctors_all/', views.DoctorListView.as_view(), name='doctors_all'),
    path('doctor_history/', views.DoctorHistoryListView.as_view(), name='doctor_history'),
    path('doctor_history_all/', views.DoctorAllHistoryListView.as_view(), name='doctor_history_all'),
    path('doctor_answer/<int:appointment_id>/', views.DoctorAnswerView.as_view(), name='doctor_answer'),

    path('analyzes/', views.TagsAnalizeView.as_view(), name='analyzes'),
    path('mrt/', views.TagsMrtView.as_view(), name='mrt'),
    path('kt/', views.TagsKtView.as_view(), name='kt'),

]
