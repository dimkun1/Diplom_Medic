from django.core.exceptions import ValidationError
from django.contrib import admin
from hospital_app.models import Appointment
from django.contrib import messages
from django.contrib.auth import get_user_model
from django import forms


class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'

    doctor = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Doctors'),
        label='Доктор'
    )
    patient = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Patient'),
        label='Пациент'
    )


class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentAdminForm
    fields = ['doctor', 'patient', 'start_date_time', 'end_date_time', 'complaint', 'readings']
    readonly_fields = ['end_date_time']
    list_display = ['patient', 'doctor', 'start_date_time', 'end_date_time', 'complaint', 'readings']
    list_display_links = ('patient', 'doctor',)
    list_filter = ['patient', 'doctor']

    def get_readonly_fields(self, request, obj=None):
        # Если пользователь является доктором, то поле complaint становится только для чтения
        if request.user.groups.filter(name='Doctors').exists():
            return ['complaint']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            for message in e.messages:
                messages.error(request, message)
            return


admin.site.register(Appointment, AppointmentAdmin)
