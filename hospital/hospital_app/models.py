from django.contrib.auth import get_user_model
from django.db import models
from datetime import timedelta

from django.core.validators import RegexValidator


class RussianLettersValidator(RegexValidator):
    def __init__(self, *args, **kwargs):
        regex = '^[А-Яа-яЁё,.!@#$%^&*()0-9 ]+$'
        message = 'только русские буквы'
        code = 'invalid_name'
        super().__init__(regex=regex, message=message, code=code, *args, **kwargs)


class Appointment(models.Model):
    patient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='patient_visits',
                                verbose_name='Пациент')
    doctor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='doctor_visits',
                               verbose_name='Доктор')
    start_date_time = models.DateTimeField(verbose_name='Начало приёма')
    end_date_time = models.DateTimeField(verbose_name='Звершение приёма')
    complaint = models.CharField(max_length=500, validators=[RussianLettersValidator()],
                                 blank=True, verbose_name='Жалобы')
    readings = models.TextField(blank=True, validators=[RussianLettersValidator()], verbose_name="Ответ доктора")

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем end_date_time только если он не был задан
        if self.end_date_time is None or not self.end_date_time:
            self.end_date_time = self.start_date_time + timedelta(minutes=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} with {self.doctor} from {self.start_date_time} to {self.end_date_time}"
