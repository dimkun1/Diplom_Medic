from collections import OrderedDict
from django.contrib.auth import get_user_model
from django.forms import DateTimeInput
from django import forms
from .models import Appointment



class DoctorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.cat_doctor} {obj.first_name} {obj.last_name}'


class PatientNewAppointmentForm(forms.ModelForm):
    doctor = DoctorModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Doctors'),
        label='Доктор',
        widget=forms.RadioSelect(attrs={'class': 'form-input-select'})
    )

    start_date_time = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        label='Дата приёма'
    )

    complaint = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-input'}),
        label='Жалобы'
    )

    patient = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name='Patient'),
        label='Пациент',
        widget=forms.HiddenInput(),  # Используем HiddenInput, чтобы поле было скрытым на странице
    )

    patient_name = forms.CharField(
        label='Пациент',
        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-input'})
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'start_date_time', 'complaint']

    def __init__(self, *args, **kwargs):
        # Добавляем параметр request в конструктор формы
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Если пользователь аутентифицирован, устанавливаем его как пациента
        if self.request and self.request.user.is_authenticated:
            self.fields['patient'].initial = self.request.user
            self.fields['patient_name'].initial = f"{self.request.user.first_name} {self.request.user.last_name}"

        # Делаем поле "пациент" только для чтения
        self.fields['patient_name'].widget.attrs['readonly'] = True
        self.fields['patient_name'].disabled = True

        # Стилизуем выбор доктора
        self.fields['doctor'].widget.attrs['class'] = 'form-input-select'

        # Изменяем порядок полей в форме
        field_order = ['patient_name', 'doctor', 'start_date_time', 'complaint']
        self.fields = OrderedDict((key, self.fields[key]) for key in field_order)


class DoctorAnswerForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'start_date_time', 'complaint', 'readings']

    def __init__(self, *args, **kwargs):
        # Добавляем параметр appointment_id в конструктор формы
        self.request = kwargs.pop('request', None)
        self.appointment_id = kwargs.pop('appointment_id', None)
        self.patient_name = kwargs.pop('patient_name', None)
        self.doctor_name = kwargs.pop('doctor_name', None)
        super().__init__(*args, **kwargs)

        self.fields['doctor'].label = f"{self.request.user.first_name} {self.request.user.last_name}"

        # Если appointment_id передан, устанавливаем его значение в скрытое поле
        if self.appointment_id:
            self.fields['appointment_id'] = forms.CharField(
                widget=forms.HiddenInput(),
                initial=self.appointment_id,
            )

        # Делаем остальные поля только для чтения
        for field_name, field in self.fields.items():
            if field_name != 'readings':
                field.widget.attrs['readonly'] = True
                field.disabled = True
                # Применяем атрибуты class и cols/rows ко всем полям
                field.widget.attrs['class'] = 'form-input'
                if isinstance(field.widget, forms.Textarea):
                    field.widget.attrs['cols'] = 50
                    field.widget.attrs['rows'] = 5

        # Добавляем поле для отображения имени пациента
        self.fields['doctor_name'] = forms.CharField(
            label='Имя доктора',
            initial=self.doctor_name,
            widget=forms.TextInput(attrs={'readonly': True}),
            disabled=True
        )

        # Добавляем поле для отображения имени пациента
        self.fields['patient_name'] = forms.CharField(
            label='Имя пациента',
            initial=self.patient_name,
            widget=forms.TextInput(attrs={'readonly': True}),
            disabled=True
        )
        self.fields['complaint'].widget = forms.Textarea()

        # Изменяем порядок полей в форме
        field_order = ['doctor_name', 'patient_name', 'start_date_time', 'complaint', 'readings']
        self.fields = OrderedDict((key, self.fields[key]) for key in field_order)
